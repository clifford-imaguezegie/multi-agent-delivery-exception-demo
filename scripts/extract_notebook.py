"""Create a privacy-conscious, read-only replay dataset from stored notebook outputs.

Usage: python scripts/extract_notebook.py /path/to/notebook.ipynb

This intentionally DOES NOT export the underlying customer database, addresses,
full internal playbook passages, or original user-facing personal names.
"""
from __future__ import annotations
import json
import re
import sys
from collections import Counter
from pathlib import Path

CELL_IDS = [306, 309, 312, 315, 318, 321, 324, 327, 330, 333]
SECTIONS = [
    "Input / Operational Context", "Predictions", "Resolution Agent Output",
    "Resolution Critic Output", "Communication Agent Output", "Communication Critic Output",
    "Metrics", "Full Workflow Trajectory", "Tool / Agent Invocation Log",
    "Final Action", "Document Citations", "Customer Message",
]
TITLES = {
    "SHP-001": "Successful delivery · routine event",
    "SHP-002": "Second failed attempt · VIP reschedule",
    "SHP-003": "Address issue · reschedule",
    "SHP-004": "Damaged fragile package · VIP replacement",
    "SHP-005": "Third failed attempt · locker constraint",
    "SHP-006": "Refused delivery · return to sender",
    "SHP-007": "Perishable weather delay · VIP replacement",
    "SHP-008": "Repeat exceptions · discretionary escalation",
    "SHP-009": "Severely damaged perishable · replacement",
    "SHP-010": "Routine depot scan · noise filtering",
}


def section(body: str, title: str) -> str:
    head = f"--- {title} ---"
    start = body.find(head)
    if start == -1:
        return ""
    rest = body[start + len(head):]
    boundaries = [rest.find(f"--- {other} ---") for other in SECTIONS if other != title]
    boundaries += [rest.find("==========================================================================================")]
    boundaries = [b for b in boundaries if b >= 0]
    return rest[:min(boundaries) if boundaries else None].strip()


def extract_jsons(s: str, count: int) -> list:
    d = json.JSONDecoder()
    pos = 0
    found = []
    for _ in range(count):
        while pos < len(s) and s[pos] not in "{[":
            pos += 1
        if pos == len(s):
            found.append({})
            continue
        try:
            value, n = d.raw_decode(s[pos:])
            found.append(value)
            pos += n
        except ValueError:
            found.append({})
            pos += 1
    return found


def extract_section_obj(body: str, key: str):
    v = extract_jsons(section(body, key), 1)
    return v[0] if v else {}


def get_field(label: str, body: str, default=None):
    found = re.search(r"^\s*" + re.escape(label) + r":\s*(.*?)\s*$", body, re.M)
    return (found.group(1) if found else default)


def scrub_text(s: str) -> str:
    if not s:
        return ""
    # Redact sample street/building locators even if referenced in agent explanations.
    s = re.sub(r"\bbuilding\s+\d+\s+on\s+[A-Z][a-zA-Z ]+?(?:Avenue|Road|Street|Lane|Drive|Close)\b", "the specified building address", s, flags=re.I)
    s = re.sub(r"\bbuilding\s+\d+\b", "the specified building", s, flags=re.I)
    s = re.sub(r"\b[A-Z][a-zA-Z]+\s+(?:Avenue|Road|Street|Lane|Drive|Close)\b", "[STREET REDACTED]", s)
    s = re.sub(r"\bservice credit of \d+(?:\.\d+)?\b", "service credit [amount redacted]", s, flags=re.I)
    # Replace named recipient salutations in draft communications.
    s = re.sub(r"(?im)\b(Dear|Hello|Hi)\s+[^\n,]{2,75}(?=,)", r"\1 Customer", s)
    # Prevent accidental disclosure of emails, phone numbers, internal customer IDs and zip-code tool arguments.
    s = re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL REDACTED]", s, flags=re.I)
    s = re.sub(r"\bCUST-\d+\b", "[CUSTOMER ID REDACTED]", s, flags=re.I)
    s = re.sub(r"check_locker_availability\(\d{5},", "check_locker_availability([AREA REDACTED],", s)
    s = re.sub(r"\b\d{1,5}\s+[A-Z][a-zA-Z.]+(?:\s+[A-Za-z.]+){0,3}\s+(?:Road|Street|Lane|Avenue|Drive|Close|Rd|St)\b", "[ADDRESS REDACTED]", s)
    # Generic contact numbers with punctuation, avoiding short numeric counts.
    s = re.sub(r"(?<![A-Za-z0-9])\+?\d[\d ()-]{8,}\d\b", "[PHONE REDACTED]", s)
    return s


def run(notebook: Path, dest: Path):
    nb = json.loads(notebook.read_text(encoding="utf-8"))
    extracted = []
    for idx in CELL_IDS:
        c = nb["cells"][idx]
        streams = ["".join(o.get("text", [])) for o in c.get("outputs", []) if o.get("output_type") == "stream"]
        whole = "\n".join(streams)
        marker = "--- Input / Operational Context ---"
        assert marker in whole, f"No operational context in cell {idx}"
        body = whole[whole.index(marker):]
        shipment_id = "SHP-%03d" % (CELL_IDS.index(idx) + 1)
        assert shipment_id in whole
        context = section(body, "Input / Operational Context")
        event, customer, escalation = extract_jsons(context, 3)
        resolution = extract_section_obj(body, "Resolution Agent Output")
        critic_resolution = extract_section_obj(body, "Resolution Critic Output")
        communication = extract_section_obj(body, "Communication Agent Output")
        critic_communication = extract_section_obj(body, "Communication Critic Output")
        final_actions = extract_section_obj(body, "Final Action")
        final = final_actions[0] if isinstance(final_actions, list) and final_actions else {}
        assert final.get("shipment_id") == shipment_id, (idx, final)
        metrics = section(body, "Metrics")
        pred = section(body, "Predictions")
        pred_match = re.search(r"Exception:\s+(\S+)\s+\(GT: (\S+)\)", pred)
        gt_resolution = re.search(r"Resolution:\s+(.+?)\s+\(GT: (.*?)\)", pred)
        gt_esc = re.search(r"Escalated:\s+(.+?)\s+\(GT: (.*?)\)", pred)
        gt_tone = re.search(r"Tone:\s+(.+?)\s+\(GT: (.*?)\)", pred)
        assert pred_match and gt_resolution and gt_esc and gt_tone, (shipment_id, pred)
        outcome = {"exception": pred_match.group(2), "resolution": gt_resolution.group(2), "escalation": gt_esc.group(2), "tone": gt_tone.group(2)}
        trajectory_lines = [a.strip() for a in section(body, "Full Workflow Trajectory").splitlines() if a.strip()]
        # Preserve actual trace steps, but rewrite one message-bearing finalize line as a minimal fact summary.
        traj = []
        for step in trajectory_lines:
            if step.startswith("finalize: actions="):
                step = f"finalize: recorded action={final.get('resolution')}, escalated={str(final.get('escalated')).lower()}, revisions={final.get('revision_count')}"
            traj.append(scrub_text(step))
        tools = [scrub_text(a.strip()) for a in section(body, "Tool / Agent Invocation Log").splitlines() if a.strip()]
        citations = re.findall(r"Page \d+", section(body, "Document Citations"))
        # Retrieval metadata only, since the PDF states Internal Use Only.
        retrieved_context = whole.split("RETRIEVED PLAYBOOK CONTEXT", 1)[1].split("COMPLETE WORKFLOW RESULT", 1)[0] if "RETRIEVED PLAYBOOK CONTEXT" in whole else ""
        references = []
        for m in re.finditer(r"\[Retrieved Chunk \d+\]\s*Page\s*:\s*(\d+)\s*Chunk ID\s*:\s*(playbook_chunk_\d+)", retrieved_context):
            references.append({"page": int(m.group(1)), "chunk_id": m.group(2)})
        # Keep only non-PII operational fields; do not export original addresses/ids.
        event = {k: scrub_text(str(event[k])) if isinstance(event.get(k), str) else event.get(k) for k in (
            "status_code", "status_description", "attempt_number", "prior_attempt_notes", "package_type", "package_size") if k in event}
        customer = {k: customer.get(k) for k in ("tier", "preferred_channel", "exceptions_last_90d") if k in customer}
        esc = {k: escalation.get(k) for k in ("has_triggers", "trigger_count") if k in escalation}
        esc["triggers"] = [scrub_text(t) for t in escalation.get("triggers", [])]
        esc["resolution_constraints"] = [scrub_text(t) for t in escalation.get("resolution_constraints", [])]
        esc["operational_constraints"] = [scrub_text(t) for t in escalation.get("operational_constraints", [])]
        decision = scrub_text(resolution.get("rationale", ""))
        resolution_data = {k: resolution.get(k) for k in ("is_exception", "resolution", "operational_action")}
        resolution_data["rationale"] = decision
        critic_data = {"decision": critic_resolution.get("decision", ""), "rationale": scrub_text(critic_resolution.get("rationale", ""))}
        comm_data = {"tone_label": communication.get("tone_label"), "communication_message": scrub_text(communication.get("communication_message", ""))}
        comm_critic_data = {"decision": critic_communication.get("decision", ""), "rationale": scrub_text(critic_communication.get("rationale", ""))}
        latency_match = re.search(r"Latency:\s+([\d.]+)s", metrics)
        coherence_match = re.search(r"Coherence Score:\s+([\d.]+)/5", metrics)
        revisions = re.search(r"Revisions:\s+(\d+)", pred)
        coherence_reason = get_field("Coherence Reason", metrics, "")
        score = float(coherence_match.group(1)) if coherence_match else None
        assert latency_match and score is not None and revisions, (shipment_id,metrics)
        datum = {
            "id": shipment_id,
            "title": TITLES[shipment_id],
            "event": event,
            "customer": customer,
            "escalation_signals": esc,
            "ground_truth": outcome,
            "final_action": {"is_exception": final.get("is_exception"), "resolution": final.get("resolution"),
                "escalated": final.get("escalated"), "tone": final.get("tone"),
                "revision_count": final.get("revision_count"), "guardrail_blocked": final.get("guardrail_blocked")},
            "resolution_agent": resolution_data,
            "resolution_critic": critic_data,
            "communication_agent": comm_data,
            "communication_critic": comm_critic_data,
            "metrics": {"task_completion": get_field("Task Complete", metrics) == "PASS",
                "exception_correct": get_field("Exception ID", metrics) == "PASS",
                "resolution_correct": get_field("Resolution", metrics) == "PASS",
                "tone_correct": get_field("Tone", metrics) == "PASS",
                "escalation_correct": get_field("Escalation Accuracy", metrics),
                "tool_call_correct": get_field("Tool Call Accuracy", metrics) == "PASS",
                "coherence_score": score, "coherence_justification": scrub_text(coherence_reason),
                "latency_seconds": float(latency_match.group(1))},
            "trajectory": traj,
            "tool_calls": tools,
            "playbook_references": references,
            "citation_pages": citations,
        }
        assert len(traj)>=2, (shipment_id,traj)
        extracted.append(datum)
    # Stored notebook aggregate is canonical; case latency values are rounded to 2dp in print.
    result = {
        "dataset_label": "Recorded notebook execution (10 benchmark scenarios)",
        "source": notebook.name,
        "replay_mode": True,
        "privacy": "Names and direct identifiers redacted; playbook source content withheld; replay only.",
        "aggregate": {"cases":10, "task_completion_percent":100, "tool_call_percent":100,
            "escalation_accuracy_percent":100,"escalation_accuracy_denominator":8,
            "escalation_routing_percent":100,"escalation_routing_denominator":10,
            "mean_coherence_out_of_5":5.0,"mean_latency_seconds":13.86},
        "cases": extracted,
    }
    assert len(extracted) == 10
    assert sum(c["metrics"]["task_completion"] for c in extracted) == 10
    assert sum(c["metrics"]["tool_call_correct"] for c in extracted) == 10
    assert round(sum(c["metrics"]["latency_seconds"] for c in extracted)/10,2)==13.86
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Extracted {len(extracted)} cases into {dest} ({dest.stat().st_size:,} bytes)")
    for c in extracted:
        print(c['id'], c['final_action']['resolution'], 'rev',c['final_action']['revision_count'],'steps',len(c['trajectory']), 'time',c['metrics']['latency_seconds'])


if __name__ == "__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python scripts/extract_notebook.py /path/to/notebook.ipynb")
    root = Path(__file__).resolve().parents[1]
    run(Path(sys.argv[1]),root/'data'/'recorded_cases.json')
