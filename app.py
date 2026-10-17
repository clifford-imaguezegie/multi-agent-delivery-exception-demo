"""Delivery Exception AI | Editorial showcase of recorded LangGraph executions.

All demonstration content is read-only. This app never runs the original agents,
invokes an API, retrieves a private document, or takes a shipment action.
"""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from replay_data import evaluation_rows, load_data
from storyline import story_scenes
from oversight_status import oversight_status
from decision_package import decision_package, label as action_label
from agent_flow import trace_steps, build_replay_html
from review_evidence import critic_timeline, communication_authority

APP_VERSION = "2.3.4"
TRACE_BATCH_LABEL = "17 October 2026"
ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Exception / Control — Multi-Agent Delivery AI", page_icon="🟠", layout="wide", initial_sidebar_state="collapsed")
st.markdown((ROOT / "style.css").read_text(encoding="utf-8"), unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_data()

records = get_data()
cases = records["cases"]
case_by_id = {c["id"]: c for c in cases}
exception_cases = [c for c in cases if c["final_action"]["is_exception"] == "YES"]
mean_exception_seconds = sum(c["metrics"]["latency_seconds"] for c in exception_cases) / len(exception_cases)


def html(value) -> str:
    return escape(str(value), quote=True)


def brand():
    st.markdown('''<div class="brand"><div class="brandmark"><span class="brandicon">E / C</span><span>EXCEPTION / CONTROL<br><span style="font-size:.67rem;color:#897581;font-weight:500;letter-spacing:.05em">A MULTI-AGENT AI ENGINEERING STORY</span></span></div><div class="brandright">PROOF OF CONCEPT &nbsp; / &nbsp; RECORDED REPLAY &nbsp; / &nbsp; 2026</div></div>''', unsafe_allow_html=True)


def hero(kicker, title, description):
    st.markdown(f'<section class="hero"><div class="eyebrow">{html(kicker)}</div><h1>{html(title)}</h1><p class="lead">{html(description)}</p></section>', unsafe_allow_html=True)


def heading(kicker, title):
    st.markdown(f'<div class="section-eyebrow">{html(kicker)}</div><div class="section-title">{html(title)}</div>', unsafe_allow_html=True)


def note(extra=""):
    st.markdown('<div class="feature"><strong>What you are viewing:</strong> A replay of ten original, stored notebook benchmark runs—not a live logistics system. No AI inference, external APIs, customer messages, or shipment actions occur here. '+html(extra)+'</div>', unsafe_allow_html=True)


def card(num, title, description):
    st.markdown(f'<div class="card"><div class="number">{html(num)}</div><h3>{html(title)}</h3><p>{html(description)}</p></div>', unsafe_allow_html=True)


def kpi(value, label, description):
    st.markdown(f'<div class="kpi"><div class="label">{html(label)}</div><div class="value">{html(value)}</div><div class="desc">{html(description)}</div></div>', unsafe_allow_html=True)


def kpi_grid():
    cols=st.columns(4, gap="small")
    items=[
        (f"{records['aggregate']['mean_latency_seconds']:.2f}s", "All 10 captured cases", "Mean LangSmith root duration"),
        (f"{mean_exception_seconds:.2f}s", "8 exception cases", "Mean exception-run duration"),
        ("10 / 10", "Runs captured", "Ten complete root traces"),
        (str(records['aggregate']['total_spans']), "Trace spans", "Across ten saved runs"),
    ]
    for column,(v,l,d) in zip(cols,items):
        with column:kpi(v,l,d)


def challenge():
    hero("The challenge / Last-mile delivery", "A failed delivery isn't one problem. It's five decisions.",
         "When a delivery goes wrong, teams must interpret messy status events, inspect customer and package context, consult policy, choose an action, and decide whether a human must intervene—all before communicating with the customer.")
    heading("01 / THE OPERATIONAL FRICTION", "Why exceptions are hard to resolve")
    cols=st.columns(3, gap="medium")
    items=[
        ("01 — SIGNAL", "Identify the real issue", "Delivery feeds contain duplicates, routine scans, failed attempts, damage reports and free-text driver notes. Not every event needs an AI agent."),
        ("02 — DECISION", "Balance competing constraints", "The correct resolution may depend on delivery history, customer tier, package fragility, perishability, address validity and locker capacity."),
        ("03 — GOVERNANCE", "Know when to escalate", "A recommendation may need revision, customer communication must be checked, and high-risk decisions require a supervisor rather than unchecked automation."),
    ]
    for col,item in zip(cols,items):
        with col:card(*item)
    heading("02 / THE SOLUTION", "A coordinated decision workflow—not a chatbot")
    cols=st.columns([1.06,.94],gap="large")
    with cols[0]:
        st.markdown("""The completed proof of concept uses **LangGraph orchestration** to combine a deterministic fast path with AI agents for complex exceptions. Agents consult operational data and a RAG-retrieved playbook, propose a resolution, independently critique it, prepare and validate customer communication, and apply human escalation rules.

This creates a recorded decision trail rather than a standalone generated answer. The proposed actions include **reschedule, reroute to locker, replace, and return to sender**. An *operational action* and an *escalation requirement* are recorded separately from the final resolution.""")
    with cols[1]:
        st.markdown('''<div class="card" style="background:#FFF0E5;border-color:#EDCEBD;min-height:210px"><div class="number">THE OPERATING PRINCIPLE</div><h3 style="font-size:1.35rem">Use judgement where needed.<br>Rules where possible.<br>People where required.</h3><p>Routine events bypass LLM processing. Genuine exceptions receive context-aware recommendations and independent checks. Defined risk or failed validation sends the case to a supervisor.</p></div>''', unsafe_allow_html=True)
    heading("03 / THE EVIDENCE", "What the completed benchmark shows")
    kpi_grid()
    st.caption(f"The fresh October 17 capture averages {records['aggregate']['mean_latency_seconds']:.2f} seconds across ten cases and {mean_exception_seconds:.2f} seconds across eight exceptions. Two routine events followed the deterministic fast path. Current-run benchmark scores are sourced separately from the executed notebook, not inferred from LangSmith durations. These results are not manual-versus-AI savings or production SLAs.")
    st.markdown('''<div class="feature"><strong>Start with a real example:</strong> SHP-003 shows a correct reschedule decision without human escalation. SHP-004 shows two Critic revisions and a separate supervisor escalation. SHP-006 and SHP-008 demonstrate a Critic objection followed by an accepted revision.</div>''',unsafe_allow_html=True)


def arch_node(text, sub="", klass=""):
    return f'<div class="arch-node {klass}">{html(text)}<small>{html(sub)}</small></div>'


def arch_row(nodes):
    return '<div class="arch-row">'+''.join(arch_node(*n) for n in nodes)+'</div>'


def architecture():
    hero("Inside the system / Implemented in the notebook", "Seven workflow steps. Two models. One accountable system.",
         "A layered view of the implemented LangGraph graph, its operational tools, knowledge retrieval, independent Critic checks and human escalation path.")
    heading("01 / END-TO-END ARCHITECTURE", "From operational signals to reviewed decisions")
    parts=['<div class="arch">', '<div class="layer">Input &amp; knowledge systems</div>',
           arch_row([("Delivery-status logs", "CSV · multi-row events" ,""), ("Customer & locker records", "SQLite · lookups", ""), ("Exception playbook", "PDF → embeddings → Chroma", "gold")]),
           '<div class="arch-down">↓</div>',
           '<div class="layer">Preparation &amp; tool services</div>',
           arch_row([("Deterministic preprocessing", "De-duplicate · classify · guardrails", "orange"), ("LangChain tools + RAG", "Record lookups · playbook context", "")]),
           '<div class="arch-down">↓</div>',
           '<div class="layer">LangGraph orchestration · conditional routing</div>',
           arch_row([("Routine fast path", "Noise / delivered → finalise", "gold"), ("Orchestrator", "Exception → agents / critics", "plum")]),
           '<div class="arch-down">↓</div>',
           '<div class="layer">Resolution loop · generation + independent review</div>',
           arch_row([("Resolution Agent", "Gemma 4 26B A4B IT · proposes action", "orange"), ("Resolution Critic", "Gemma 4 31B IT · accept / revise / escalate", "soft")]),
           '<div class="arch-callout"><strong>Feedback loop:</strong> Critic can return a resolution for revision. The orchestrator caps resolution revisions at two; unresolved cases are escalated rather than looping indefinitely.</div>',
           '<div class="arch-down">↓</div>',
           '<div class="layer">Customer communication · generation + independent review</div>',
           arch_row([("Communication Agent", "Gemma 4 26B A4B IT · drafts message", "orange"), ("Communication Critic", "Gemma 4 31B IT · checks content", "soft")]),
           '<div class="arch-down">↓</div>',
           '<div class="layer">Governance &amp; finalisation</div>',
           arch_row([("Policy escalation", "Automatic / discretionary human review", "gold"), ("Final decision record", "Resolution · operational action · escalation · draft", "plum")]),
           '<div class="arch-callout"><strong>Cross-cutting observability:</strong> LangSmith traces the original notebook workflow; the public app only replays anonymised captured outputs, not live LangSmith traces.</div>',
           '<div class="arch-details">Architecture reconstructed from the implementation architecture, model-role mapping, tools, state transitions and recorded executions in the uploaded notebook.</div>',
           '</div>']
    st.markdown('\n'.join(parts), unsafe_allow_html=True)
    heading("02 / RESPONSIBILITIES", "Why each component exists")
    entries=[
        ("Preprocessor & guardrails", "Normalises raw events, removes duplicates, separates routine activity from actionable exceptions and enforces structured checks."),
        ("Orchestrator (LangGraph)", "Routes work based on state and Critic outcomes; manages bounded revision loops and escalation logic."),
        ("Resolution Agent", "Uses operational context, tools and retrieved playbook guidance to recommend an action and operational handling."),
        ("Resolution Critic", "Independently assesses the recommendation, requests correction, accepts or triggers escalation conditions."),
        ("Communication Agent & Critic", "Produces a customer-appropriate draft and evaluates its quality before finalisation; no messages are sent by this demo."),
        ("Finalisation & LangSmith", "Captures the final decision and its trace for evaluation and human review; observability occurred during the latest recorded runs."),
    ]
    cols=st.columns(2,gap="medium")
    for i,(title,body) in enumerate(entries):
        with cols[i%2]:card(f"{i+1:02d}",title,body)
    st.info("This architecture represents the original implemented multi-agent system. The public Streamlit app is a separate read-only replay built from saved traces and results. It does not host the agents or the underlying SQLite, PDF, Chroma or model services.")


def case_selector():
    return st.selectbox("Choose a recorded shipment", options=list(case_by_id),
        format_func=lambda s:f"{s}  ·  {case_by_id[s]['title']}",
        index=3, key="selected_case_id")


def render_event_line(line: str, number: int | None = None):
    number_prefix=f'<strong>{number:02d} &nbsp;</strong>' if number is not None else ''
    st.markdown(f'<div class="event-card">{number_prefix}{html(line)}</div>',unsafe_allow_html=True)


def case_summary(case):
    final=case["final_action"]
    flag="ESCALATION REQUESTED" if final["escalated"] else "NO ESCALATION REQUESTED"
    st.markdown(f'<div class="case-banner"><strong>{html(case["id"])} &nbsp; / &nbsp; {html(case["title"])}</strong><br><span style="font-size:.85rem">{html(case["event"].get("status_code","—"))} &nbsp; · &nbsp; {html(final["resolution"].replace("_"," "))} &nbsp; · &nbsp; {html(flag)} &nbsp; · &nbsp; {case["metrics"]["latency_seconds"]:.2f}s recorded</span></div>',unsafe_allow_html=True)


def show_decision_package(case):
    package = decision_package(case)
    heading("THE FULL OUTCOME", "More than a resolution label")
    sections = [
        ("01 / RESOLUTION", "Primary resolution", package["primary"]),
        ("02 / HANDLING", "Operational instruction", package["operational"]),
        ("03 / CUSTOMER", "Customer communication", package["customer"]),
        ("04 / GOVERNANCE", "Supervisor decision", package["supervisor"]),
    ]
    cols=st.columns(4, gap="small")
    for col,(num,title,value) in zip(cols,sections):
        with col:
            st.markdown(f'<div class="decision-card"><div class="number">{html(num)}</div><div class="decision-head">{html(title)}</div><p>{html(value)}</p></div>',unsafe_allow_html=True)
    oversight=oversight_status(case)
    with st.expander("Recorded oversight outcome and explanation", expanded=True):
        st.markdown(f"**{oversight['headline']}**")
        st.write(oversight['explanation'])
        for reason in oversight['reasons']:
            st.write("• "+reason)
        if oversight['benchmark_disagrees']:
            expected='YES' if oversight['benchmark_expected'] else 'NO'
            actual='YES' if oversight['escalated'] else 'NO'
            st.warning(f"**Benchmark discrepancy:** recorded escalation = {actual}; expected ground-truth escalation = {expected}. This is a result of this captured AI execution, not a display error or verified correct decision.")
    st.caption("All outcomes are recorded recommendations, handling instructions, draft communications and routing decisions. The replay does not execute deliveries, contact customers or notify supervisors.")



def show_critic_audit(case:dict):
    audit=critic_timeline(case)
    reviews=audit['resolution_reviews']
    heading("REVIEW HISTORY", "The objection, the proposal and what changed")
    if not reviews:
        st.info("Routine fast path: no Resolution Critic was invoked.")
        return
    st.caption("These are privacy-redacted outputs of the NEW October 17 LangSmith capture. Individual elapsed times come from recorded span timestamps. A Critic ACCEPT does not independently establish operational correctness.")
    for r in reviews:
        proposal=r.get('proposal') or {}
        st.markdown(f'<div class="review-card"><div class="review-index">RESOLUTION REVIEW {r["sequence"]:02d} · STAGE {r["trace_index"]:02d} · {r["duration_seconds"]:.3f}s measured</div><div class="review-decision {html(r["verdict"].lower())}">{html(r["verdict"])}</div><div class="review-proposal">Proposed resolution: <b>{html(proposal.get("resolution") or "Not recorded")}</b></div><div class="review-proposal">Operational instruction: <b>{html(proposal.get("operational_action") or "Not recorded")}</b></div></div>',unsafe_allow_html=True)
        if proposal.get('rationale'):
            with st.expander(f"Proposal {r['sequence']} — Resolution Agent's rationale",expanded=r['verdict']=='REVISE'):
                st.write(proposal['rationale'])
        if r['rationale']:
            st.markdown('**Critic rationale (captured):**')
            st.write(r['rationale'])
        else:st.caption('The Critic verdict was captured without a rationale for this stage.')
    if audit['orchestrator_override']['present']:
        st.warning('The final ESCALATE field was an Orchestrator revision-limit override, not an additional independent Critic decision.')
    if audit['communication_reviews']:
        st.markdown('#### Communication Critic and draft assessment')
        for r in audit['communication_reviews']:
            st.write(f"**Communication review {r['sequence']} · {r['verdict']} · {r['duration_seconds']:.3f}s**")
            with st.expander('Review the associated unsent draft and feedback'):
                st.write('**Draft reviewed:**')
                st.text(r.get('reviewed_draft',{}).get('communication_message','Not retained'))
                st.write('**Critic assessment:**')
                st.write(r['rationale'] or 'No recorded rationale')
    st.caption('All evidence is from the current recorded run. Supervisor authorisation and real customer notification were not executed or verified.')


def show_communication_caveat(case: dict):
    authority=communication_authority(case)
    if not authority['draft_available']:
        return
    st.markdown(f'<div class="authority-note"><strong>{html(authority["status"])}</strong><p>{html(authority["caution"])}</p></div>',unsafe_allow_html=True)
    if authority['model_gap']:
        st.warning('**Recorded decision-model limitation:** '+authority['model_gap'])
    if authority['specific_risk']:
        st.warning('**Communication governance concern:** '+authority['specific_risk'])


def stories():
    hero("The case stories / October 17 recorded runs", "Follow a decision. See what the agents really did.",
         "Explore scenario-based narratives reconstructed from the October 17 LangSmith stage traces. The stories explain each decision, while the full chronological event sequence remains available for inspection.")
    note("The guided chapters are editorial summaries of captured evidence, not individual recorded event timestamps.")
    heading("01 / CHOOSE YOUR CASE", "Ten recorded decisions, different operating challenges")
    case=case_by_id[case_selector()]
    case_summary(case)
    show_decision_package(case)
    left,right=st.columns([1.6,1],gap="large")
    with left:
        st.markdown('''<div class="section-eyebrow">02 / GUIDED STORY</div>''',unsafe_allow_html=True)
        scenes=story_scenes(case)
        key="scene_"+case["id"]
        st.session_state.setdefault(key,0)
        current=max(0,min(st.session_state[key],len(scenes)-1))
        scene=scenes[current]
        st.markdown(f'<div class="scene"><div class="chapter">{html(scene["label"])} &nbsp; · &nbsp; CHAPTER {current+1} OF {len(scenes)}</div><h2>{html(scene["title"])}</h2><p>{html(scene["summary"])}</p><div class="scenefoot">EDITED STORY FROM SAVED RECORDS · PER-AGENT TIMINGS AVAILABLE IN AGENT FLOW</div></div>',unsafe_allow_html=True)
        a,b,c=st.columns([1,1,1],gap="small")
        with a:
            if st.button("↺ First chapter",use_container_width=True,key="first",disabled=current==0):
                st.session_state[key]=0;st.rerun()
        with b:
            if st.button("← Back",use_container_width=True,key="back",disabled=current==0):
                st.session_state[key]=current-1;st.rerun()
        with c:
            if st.button("Next chapter →",type="primary",use_container_width=True,key="next",disabled=current>=len(scenes)-1):
                st.session_state[key]=current+1;st.rerun()
        st.progress((current+1)/len(scenes),text=f"Guided story: chapter {current+1} / {len(scenes)}")
    with right:
        st.markdown("#### Evidence behind this chapter")
        st.caption("Every entry below comes from the stored current run’s privacy-redacted trace.")
        if scene["evidence"]:
            for line in scene["evidence"][:10]:render_event_line(line)
            if len(scene["evidence"])>10:st.caption(f"{len(scene['evidence'])-10} further events in the full trace below.")
        else:st.info("No agent execution needed for this stage.")
        f=case["final_action"]
        a,b=st.columns(2)
        a.metric("Resolution revisions",f["revision_count"])
        b.metric("Recorded runtime",f'{case["metrics"]["latency_seconds"]:.2f}s')
    with st.expander("Inspect the independent review timeline — with recovered LangSmith evidence"):
        show_critic_audit(case)
        show_communication_caveat(case)
    with st.expander("Privacy-redacted chronological LangSmith stage sequence"):
        for i,line in enumerate(case["trajectory"],1):render_event_line(line,i)
        st.caption("These are privacy-redacted summaries of the new LangSmith stage sequence. Actual stage durations and start offsets appear in Agent flow.")
    st.markdown('**Want to see the actual back-and-forth?** Open the **Agent flow** workspace to watch the recorded events move between agents, including revision loops.\n')
    heading("03 / THE FILM", "Watch the SHP-006 correction unfold")
    video=ROOT/'assets'/'shp006_story.mp4'
    a,b=st.columns([1.35,.65],gap='large')
    with a:
        if video.exists():st.video(str(video))
        else:st.warning('Edited walkthrough unavailable; the interactive Agent flow contains the full sequence.')
    with b:
        st.markdown('**One issue. A Critic objection. A corrected recommendation.**')
        st.write('This silent captioned reconstruction follows SHP-006 from its initial proposal through REVISE and final ACCEPT, then the customer communication review. It uses only the new captured execution.')
        st.caption(f"The video is an edited explanation, NOT live inference. SHP-006 took {case_by_id['SHP-006']['metrics']['latency_seconds']:.2f} seconds in this capture; film duration is separate from execution time.")


def agent_replay():
    hero("Agent flow / Captured LangSmith stages", "Follow the agents. Read exactly what they decided.",
         "Watch the actual sequence, feedback loops and customer-draft checks. The recorded duration of each agent stage accompanies its output; the moving ball is an illustrative replay, not a real-time recording.")
    note("Individual stage durations are derived from LangSmith timestamps. They include each stage's internal model or tool work and must not be added to nested span timings.")
    heading('01 / SELECT A RECORDING','Compare acceptance, revisions and escalation')
    case=case_by_id[case_selector()]
    case_summary(case)
    st.markdown('<div class="feature"><strong>Try these contrasting cases:</strong> SHP-003: resolution ACCEPT with no human escalation. SHP-004: two resolution revisions, then escalation. SHP-006 and SHP-008: REVISE followed by ACCEPT. SHP-007: Communication Critic escalated. Routine cases SHP-001 and SHP-010 bypass LLMs.</div>', unsafe_allow_html=True)
    heading('02 / AGENT-TO-AGENT REPLAY','Original stage order, captured output and measured durations')
    components.html(build_replay_html(case),height=790,scrolling=False)
    st.caption('Quick overview remains the default (6–25 seconds per event). Comfortable now allows 30–120 seconds; Extra reading time allows 60–240 seconds per event. You can pause or use Manual. These are **reading pauses**, not the measured LangSmith stage durations.')
    heading('03 / REVIEW EVIDENCE','View the original objections and revised proposals')
    show_critic_audit(case)
    show_communication_caveat(case)
    show_decision_package(case)
    with st.expander('Full redacted LangSmith stage chronology'):
        for step in trace_steps(case):render_event_line(f"+{step['offset']:.3f}s · {step['timing']:.3f}s · {step['source']}",step['index'])


def evidence():
    hero("Under the surface / Inspection room", "A decision is only as useful as its evidence.",
         "Read the anonymised tool activity, agent recommendations, independent Critic assessments, stage timings and unsent customer drafts recovered from LangSmith.")
    note("The original playbook is private. This public capture excludes all retrieved document text, internal prompts and private customer records. Recorded Critic rationales were redacted before publication.")
    case=case_by_id[case_selector()]
    case_summary(case)
    show_decision_package(case)
    errors=case['trace_summary'].get('recovered_error_spans',0)
    if errors:
        st.info(f'The original LangSmith trace recorded {errors} internal validation-error subspans which were recovered by the workflow. The case completed and its notebook assessment passed; private error details are not included in the public replay.')
    tabs=st.tabs(["Agent & Critic decisions","Critic review audit","Tools & controls","Policy provenance","Customer draft","Redacted stage history"])
    with tabs[0]:
        a,b=st.columns(2,gap="large")
        with a:
            heading("Recommendation", "Resolution Agent")
            r=case["resolution_agent"]
            st.write("**Resolution:**",r.get("resolution") or "Not invoked for routine event")
            st.write("**Operational action:**",r.get("operational_action") or "N/A")
            st.write(r.get("rationale") or "Routine event filtered without LLM resolution.")
        with b:
            heading("Final captured state", "Final Critic fields, see each review alongside")
            audit=critic_timeline(case)
            for label,key in [("Resolution Critic","resolution_critic"),("Communication Critic","communication_critic")]:
                critic=case[key]
                if key=='resolution_critic' and audit['orchestrator_override']['present']:
                    st.write('**Orchestrator-forced terminal state:**',critic.get('decision'))
                else:
                    st.write(f"**{label} — final stored result:**",critic.get("decision") or "Not invoked")
                st.write(critic.get("rationale") or "No Critic invoked for this routine event.")
            st.caption("The adjacent Critic review audit tab separates every logged decision from the terminal state. Earlier Critic rationale and the associated proposals are available in the adjacent audit tab, where captured.")
    with tabs[1]:
        show_critic_audit(case)
        show_communication_caveat(case)
    with tabs[2]:
        a,b=st.columns(2,gap="large")
        with a:
            st.subheader("Recorded tools and agent calls")
            if case["tool_calls"]:
                for i,tool in enumerate(case["tool_calls"],1):render_event_line(tool,i)
            else:st.info("No tool activity was captured for this routine event.")
        with b:
            st.subheader("Constraints and escalation")
            sig=case["escalation_signals"]
            for title,key in [("Escalation signals","triggers"),("Resolution constraints","resolution_constraints"),("Operational constraints","operational_constraints")]:
                st.write("**"+title+"**")
                for x in sig.get(key,[]):render_event_line(x)
                if not sig.get(key):st.caption("None recorded")
            st.write("**Guardrail blocked:**", "Yes" if case["final_action"].get("guardrail_blocked") else "No")
            st.write("**Resolution revision count:**", case["final_action"]["revision_count"])
    with tabs[3]:
        st.subheader("Public playbook provenance boundary")
        refs=case["playbook_references"]
        if refs:st.dataframe(pd.DataFrame(refs).rename(columns={"page":"Source page","chunk_id":"Retrieved chunk ID"}),hide_index=True,use_container_width=True)
        else:st.info("Full source-document excerpts and retrieval payloads have been intentionally omitted from the public dataset.")
        st.caption("The private LangSmith archive contains the full retrieval spans. The public application retains tool-call names and duration without publishing proprietary policy passages or customer data.")
    with tabs[4]:
        c=case["communication_agent"]
        if c.get("communication_message"):
            st.write("**Draft tone:**",c.get("tone_label") or "Not specified")
            show_communication_caveat(case)
            st.text(c["communication_message"])
            st.caption("Privacy-redacted draft from the October 17 trace. It was not sent, and no supervisor approval was recorded.")
        else:st.info("Routine event: no customer message needed.")
    with tabs[5]:
        for i,line in enumerate(case["trajectory"],1):render_event_line(line,i)
    st.download_button("Download anonymised case record (JSON)",json.dumps(case,indent=2,ensure_ascii=False),f"{case['id']}_evidence.json","application/json")


def results():
    hero("Results / Current recorded capture", "Measured traces. Clear boundaries.",
         "The latest October 17 execution has ten recorded LangSmith traces and ten individually scored notebook assessments. The captured evidence shows decisions and Critic feedback; the notebook evaluates those decisions against a curated benchmark.")
    note("The assessment results below come from the uploaded executed notebook for THIS trace batch. All ten cases passed their applicable benchmark checks, but two received lower LLM-as-a-Judge coherence scores. Curated benchmarks do not establish production accuracy or speed gains.")
    heading('01 / RECORDED EXECUTION','What LangSmith actually measured')
    kpi_grid()
    heading('02 / THE TEN CASES','Duration and outcomes in the latest execution')
    oversight_states=[oversight_status(c) for c in records['cases']]
    n_escalated=sum(x['escalated'] for x in oversight_states)
    n_routine=sum(x['routine'] for x in oversight_states)
    n_no_escalation=sum(not x['escalated'] and not x['routine'] for x in oversight_states)
    st.info(f"**Escalation breakdown:** {n_escalated} of 10 cases requested supervisor escalation; {n_no_escalation} exception(s) were handled without escalation; {n_routine} routine events bypassed agent review. Requests do not establish that a human reviewed or approved a case. These are curated scenarios, not a representative rate of escalations in live logistics operations.")
    divergent=[c['id'] for c in records['cases'] if oversight_status(c)['benchmark_disagrees']]
    if divergent:
        st.warning(f"**Recorded outcome versus expected benchmark:** {', '.join(divergent)} differed on whether supervisor escalation was needed. The captured outcome is retained and not silently corrected.")
    df=pd.DataFrame(evaluation_rows(records))
    a,b=st.columns([1.15,.85],gap='large')
    with a:
        st.bar_chart(df.set_index('Shipment')[["Latency (s)"]],height=330,color='#ED6848')
        st.caption('Root-span elapsed times from the latest capture. The two routine cases completed on the deterministic path without LLM resolution.')
    with b:
        st.markdown('#### Cases worth exploring')
        st.write(f"**SHP-003 · {case_by_id['SHP-003']['metrics']['latency_seconds']:.2f}s:** RESCHEDULE / no escalation — matches the expected benchmark outcome.")
        st.write(f"**SHP-004 · {case_by_id['SHP-004']['metrics']['latency_seconds']:.2f}s:** Two Resolution Critic REVISE decisions and human escalation; Judge coherence 3/5.")
        st.write(f"**SHP-005 · {case_by_id['SHP-005']['metrics']['latency_seconds']:.2f}s:** Locker-capacity constraint; Judge coherence 2/5.")
        st.write(f"**SHP-006 · {case_by_id['SHP-006']['metrics']['latency_seconds']:.2f}s:** REVISE → ACCEPT without human escalation.")
        st.write(f"**SHP-008 · {case_by_id['SHP-008']['metrics']['latency_seconds']:.2f}s:** REVISE → ACCEPT with discretionary escalation.")
        st.write(f"**Exception-only mean · {mean_exception_seconds:.2f}s:** Eight actionable cases, excluding two deterministic routine events.")
    heading('03 / NOTEBOOK BENCHMARK', 'Recorded decisions versus expected outcomes')
    b1,b2,b3=st.columns(3, gap='small')
    with b1:kpi('10 / 10','Task checks passed','Ten curated scenarios from the executed notebook')
    with b2:kpi('10 / 10','Tools checks passed','Notebook evaluator; not operational production validation')
    with b3:kpi(f"{records['aggregate']['judge_mean_coherence']:.1f} / 5",'Mean Judge coherence','LLM-scored; SHP-004: 3/5, SHP-005: 2/5')
    st.caption('For routine events, escalation and tone are N/A rather than PASS. Coherence is an LLM-as-a-Judge score, distinct from resolution accuracy and operational safety.')
    recovered=sum(c['trace_summary'].get('recovered_error_spans',0) for c in cases)
    if recovered:
        st.info(f'{recovered} internal model/validation error spans were captured in SHP-004; the workflow recovered and its final notebook assessment passed. These are not zero-error traces. The private error payloads are not published.')
    st.dataframe(df,hide_index=True,use_container_width=True)
    st.download_button('Export the current trace summary',df.to_csv(index=False).encode('utf-8'),'delivery_exception_trace_results.csv','text/csv')
    heading('04 / EVIDENCE MATURITY','What is and is not established')
    cols=st.columns(3)
    for col,item in zip(cols,[
        ('01','Experimental scope','Ten curated scenarios demonstrate captured processing steps and constraints, not real-world production reliability or monetary savings.'),
        ('02','Independent outcomes','The notebook scored this specific run against its curated ground truth and provided LLM-as-a-Judge coherence. These checks are not external operational certification.'),
        ('03','Decision authority','Agent ACCEPT is not customer authorisation, supervisor approval or evidence that a delivery instruction was executed.')
    ]):
        with col:card(*item)


brand()
pages=["The challenge","Architecture","Case stories","Agent flow","Evidence room","Results"]
page=st.radio("Explore",pages,horizontal=True,label_visibility="collapsed",key="view")
if page=="The challenge":challenge()
elif page=="Architecture":architecture()
elif page=="Case stories":stories()
elif page=="Agent flow":agent_replay()
elif page=="Evidence room":evidence()
else:results()
st.markdown(f'''<div class="footer-note">
  <div class="footer-description">
    <div class="footer-heading">EXCEPTION / CONTROL</div>
    <p>Completed multi-agent AI proof of concept · Recorded evidence replay.<br>
       No live inference, external API calls or real customer actions take place in this demo.</p>
  </div>
  <div class="release-tag" aria-label="Application version {APP_VERSION}">
    <div class="release-main"><span>APP VERSION</span><strong>v{APP_VERSION}</strong></div>
    <div class="release-trace">TRACE · {html(TRACE_BATCH_LABEL)}</div>
  </div>
</div>''',unsafe_allow_html=True)
