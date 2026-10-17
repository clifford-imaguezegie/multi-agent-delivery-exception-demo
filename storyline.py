"""Evidence-grounded editorial story chapters derived from the current LangSmith-recorded workflow stages.

The chapters summarize *recorded* evidence. They do not fabricate timestamps or
LLM/tool calls, and a separate full trajectory preserves the original event order.
"""
from __future__ import annotations

from oversight_status import oversight_status


def story_scenes(case: dict) -> list[dict]:
    shipment = case["id"]
    event = case["event"]
    customer = case["customer"]
    final = case["final_action"]
    trajectory = case["trajectory"]
    oversight = oversight_status(case)
    routine = oversight["routine"]
    def lines(*prefixes):
        return [line for line in trajectory if any(line.startswith(p) for p in prefixes)]

    result = [{
        "label": "01 / THE SIGNAL", "title": "A delivery event enters the workflow",
        "summary": f"{shipment} is recorded as {event.get('status_code', 'a delivery event')}. The system receives delivery notes, package attributes and customer context before making a decision.",
        "evidence": [f"Recorded event: {event.get('status_description', 'Not recorded')}",
                     f"Package: {event.get('package_type', 'N/A')} · Customer tier: {customer.get('tier', 'N/A')}"]
    },{
        "label": "02 / TRIAGE", "title": "Separate operational noise from a genuine exception",
        "summary": ("The deterministic preprocessor filters this routine event, avoiding unnecessary AI-agent and policy-retrieval calls." if routine else
                    "The preprocessor normalises the incoming event stream before handing an actionable exception to LangGraph routing."),
        "evidence": lines("preprocessor:")
    }]

    if routine:
        result.append({
            "label": "03 / FAST PATH", "title": "Close the event without agent inference",
            "summary": "No Resolution Agent, Critic or Communication Agent is needed for this routine event. The orchestrator routes directly to finalisation.",
            "evidence": lines("orchestrator:", "finalize:")
        })
    else:
        res = case["resolution_agent"]
        rv = final["revision_count"]
        cri = case["resolution_critic"]
        trigger = oversight["reasons"]
        result += [{
            "label": "03 / RECOMMENDATION", "title": "The Resolution Agent proposes a next action",
            "summary": f"The recorded recommendation is {final['resolution'].replace('_',' ').lower()}. The operational handling instruction is {res.get('operational_action') or 'not specified in the extracted record'}.",
            "evidence": lines("resolution_agent:")
        },{
            "label": "04 / INDEPENDENT CHECK", "title": "A separate Critic tests the recommendation",
            "summary": (f"The Critic requested {rv} revisions; the recorded final decision requires human escalation. The review chronology can be inspected in full." if rv == 2 and final["escalated"] else
                        f"The Critic required {rv} revision(s) before the workflow progressed." if rv else
                        f"The recorded Resolution Critic decision is {cri.get('decision','not recorded')}; no resolution revision loop was required."),
            "evidence": lines("critic_resolution:", "orchestrator: REVISE", "orchestrator: Max resolution revision") + ([f"Final Critic assessment: {cri.get('decision','not recorded')}"] if cri else [])
        },{
            "label": "05 / ESCALATION CHECK", "title": oversight["headline"],
            "summary": oversight["explanation"] + (" The recorded decision differs from the benchmark's expected escalation label." if oversight["benchmark_disagrees"] else ""),
            "evidence": (trigger or ["No final supervisor escalation requested in the recorded execution."]) + lines("orchestrator: Forced escalation", "orchestrator: Discretionary escalation")
        },{
            "label": "06 / CUSTOMER RESPONSE", "title": "Draft and review the customer communication",
            "summary": (f"A {case['communication_agent'].get('tone_label', 'selected').lower()} message is drafted, then checked by the independent Communication Critic. The replay never sends it."),
            "evidence": lines("communication_agent:", "critic_communication:")
        }]

    result.append({
        "label": f"{len(result)+1:02d} / FINAL RECORD", "title": "An auditable decision is captured",
        "summary": f"Recorded outcome: {final['resolution'].replace('_',' ')}; supervisor escalation {'requested' if final['escalated'] else 'not requested'}. No supervisor approval or customer action was executed. LangSmith root-span duration: {case['metrics']['latency_seconds']:.2f} seconds.",
        "evidence": lines("finalize:")
    })
    return result
