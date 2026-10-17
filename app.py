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
from decision_package import decision_package, label as action_label
from agent_flow import trace_steps, build_replay_html

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
        ("13.86s", "All 10 test runs", "Mean end-to-end latency"),
        (f"{mean_exception_seconds:.2f}s", "8 exception runs", "Mean exception latency"),
        ("10 / 10", "Task completion", "Curated benchmark scenarios"),
        ("5 / 5", "Coherence score", "LLM-as-a-Judge, mean")
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
    st.caption("The 13.86-second average includes two near-instant routine cases (0.02s, 0.03s). The 17.32-second mean isolates eight genuine exception scenarios; individual exception runs range from 8.41s to 32.65s. These are not manual-versus-AI time savings or production SLAs.")
    st.markdown('''<div class="feature"><strong>Start with a real example:</strong> SHP-004, a damaged fragile package, demonstrates why independent Critic review and a bounded escalation path matter. Its recorded workflow required two resolution revisions and ended in a human escalation.</div>''',unsafe_allow_html=True)


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
        ("Finalisation & LangSmith", "Captures the final decision and its trace for evaluation and human review; observability occurred during the original runs."),
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
    flag="SUPERVISOR ESCALATION" if final["escalated"] else "NO FINAL ESCALATION"
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
    if package["escalation_triggers"]:
        with st.expander("Why human review was required — recorded escalation reasons"):
            for trigger in package["escalation_triggers"]:render_event_line(trigger)
    st.caption("All outcomes are recorded recommendations, handling instructions, draft communications and routing decisions. The replay does not execute deliveries, contact customers or notify supervisors.")


def stories():
    hero("The case stories / Actual captured runs", "Follow a decision. See what the agents really did.",
         "Explore scenario-based narratives reconstructed from the original notebook traces. The stories explain each decision, while the full chronological event sequence remains available for inspection.")
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
        st.markdown(f'<div class="scene"><div class="chapter">{html(scene["label"])} &nbsp; · &nbsp; CHAPTER {current+1} OF {len(scenes)}</div><h2>{html(scene["title"])}</h2><p>{html(scene["summary"])}</p><div class="scenefoot">EDITED STORY FROM SAVED RECORDS · NO PER-STEP TIMINGS AVAILABLE</div></div>',unsafe_allow_html=True)
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
        st.caption("Every entry below comes from the stored case record or its redacted event trace.")
        if scene["evidence"]:
            for line in scene["evidence"][:10]:render_event_line(line)
            if len(scene["evidence"])>10:st.caption(f"{len(scene['evidence'])-10} further events in the full trace below.")
        else:st.info("No agent execution needed for this stage.")
        f=case["final_action"]
        a,b=st.columns(2)
        a.metric("Resolution revisions",f["revision_count"])
        b.metric("Recorded runtime",f'{case["metrics"]["latency_seconds"]:.2f}s')
    with st.expander("Original chronological event sequence — all recorded trace lines"):
        for i,line in enumerate(case["trajectory"],1):render_event_line(line,i)
        st.caption("These trace lines have original ordering, but do not contain per-node timestamps. No durations are assigned to individual steps.")
    st.markdown('**Want to see the actual back-and-forth?** Open the **Agent flow** workspace to watch the recorded events move between agents, including revision loops.\n')
    heading("03 / THE FILM", "Watch the SHP-004 decision unfold")
    video=ROOT/"assets"/"shp004_story.mp4"
    a,b=st.columns([1.35,.65],gap="large")
    with a:
        if video.exists():
            st.video(str(video))
        else:
            st.warning("Captioned walkthrough not available in this build. Use the interactive story above.")
    with b:
        st.markdown("**One damaged fragile package. Two Critic revisions. One controlled escalation.**")
        st.write("This silent, captioned walkthrough reconstructs the recorded SHP-004 case from the original test. It demonstrates input triage, the recommendation, independent Critic review, a bounded revision loop, customer message validation and the final supervised outcome.")
        st.caption("The film is an edited explanation, not a screen recording of live inference. Its duration is not the model processing time: the original SHP-004 run took 28.58 seconds.")


def agent_replay():
    hero("The agent flow / A recorded conversation between components", "Watch the decision travel. Including the return loops.",
         "Follow the actual chronological trace as control passes between preprocessing, LangGraph orchestration, specialist agents, independent Critics and finalisation. The moving indicator is an illustration of recorded event order, not live inference.")
    note("Individual agent execution timings were not captured in the original notebook. Only the measured full-case latency is shown; the animated replay runs at a viewer-controlled pace.")
    heading("01 / SELECT A RECORDING", "See the flow of decisions, revisions and escalations")
    case=case_by_id[case_selector()]
    case_summary(case)
    st.markdown('<div class="feature"><strong>Try these contrasting cases:</strong> SHP-004 shows two Critic revisions and supervisor escalation; SHP-003 shows a revision and structured-output validation retry; SHP-005 shows a locker recommendation held for supervisor review because the locker is full. SHP-001 shows why routine events skip the AI agents.</div>', unsafe_allow_html=True)
    heading("02 / LIVE-STYLE ANIMATION OF SAVED EVENTS", "Agent-to-agent execution replay")
    components.html(build_replay_html(case), height=730, scrolling=False)
    show_decision_package(case)
    with st.expander("Full chronological source trace (all events, unchanged and ordered)"):
        for step in trace_steps(case):
            render_event_line(step["source"],step["index"])
    st.caption("The motion is illustrative. The event sequence and source lines come from the anonymised recorded notebook trace. Node-level timestamps and intermediate Critic payloads were not saved; the app does not infer them.")


def evidence():
    hero("Under the surface / Inspection room", "A decision is only as useful as its evidence.",
         "Read the anonymised tool activity, agent recommendations, independent Critic assessments, policy references and unsent customer drafts recorded in the original notebook.")
    note("The original playbook was marked Internal Use Only; the public replay includes reference metadata but not private policy passages.")
    case=case_by_id[case_selector()]
    case_summary(case)
    show_decision_package(case)
    tabs=st.tabs(["Agent & Critic decisions","Tools & controls","Policy provenance","Customer draft","Raw event history"])
    with tabs[0]:
        a,b=st.columns(2,gap="large")
        with a:
            heading("Recommendation", "Resolution Agent")
            r=case["resolution_agent"]
            st.write("**Resolution:**",r.get("resolution") or "Not invoked for routine event")
            st.write("**Operational action:**",r.get("operational_action") or "N/A")
            st.write(r.get("rationale") or "Routine event filtered without LLM resolution.")
        with b:
            heading("Independent checks", "Critic assessments")
            for label,key in [("Resolution Critic","resolution_critic"),("Communication Critic","communication_critic")]:
                critic=case[key]
                st.write(f"**{label}:**",critic.get("decision") or "Not invoked")
                st.write(critic.get("rationale") or "No Critic invoked for this routine event.")
            st.caption("An intermediate REVISE can appear in the original chronological trace even when the final Critic decision is ACCEPT. Full per-iteration payloads were not preserved.")
    with tabs[1]:
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
    with tabs[2]:
        st.subheader("Retrieved source references")
        refs=case["playbook_references"]
        if refs:st.dataframe(pd.DataFrame(refs).rename(columns={"page":"Source page","chunk_id":"Retrieved chunk ID"}),hide_index=True,use_container_width=True)
        else:st.info("No playbook retrieval required for this routine event.")
        st.caption("Source pages and chunk identifiers show provenance without reproducing the private playbook. References do not verify the underlying passages to outside visitors.")
    with tabs[3]:
        c=case["communication_agent"]
        if c.get("communication_message"):
            st.write("**Draft tone:**",c.get("tone_label") or "Not specified")
            st.text(c["communication_message"])
            st.caption("Anonymised historic draft, not sent to a customer.")
        else:st.info("Routine event: no customer message needed.")
    with tabs[4]:
        for i,line in enumerate(case["trajectory"],1):render_event_line(line,i)
    st.download_button("Download anonymised case record (JSON)",json.dumps(case,indent=2,ensure_ascii=False),f"{case['id']}_evidence.json","application/json")


def results():
    hero("Results / The benchmark, not the hype", "Show the outcome. Show the limitations.",
         "Ten curated notebook scenarios were assessed for correct completion, tool usage, escalation, decision coherence and whole-workflow latency.")
    note("These metrics are not representative production performance, reliability SLAs or demonstrated savings compared with a manual baseline.")
    heading("01 / PERFORMANCE", "What was measured")
    kpi_grid()
    cols=st.columns(3)
    with cols[0]:kpi("10 / 10", "Tool-call correctness", "All curated scenarios")
    with cols[1]:kpi("8 / 8", "Escalation accuracy", "Applicable exception labels")
    with cols[2]:kpi("10 / 10", "Escalation routing", "Includes two routine cases")
    st.caption("The coherence scores were evaluated by an LLM-as-a-Judge; the original notebook reported 5/5 in all ten cases. Results have not been independently audited on live operations.")
    heading("02 / CASE-LEVEL RESULTS", "The longer cases tell the interesting story")
    df=pd.DataFrame(evaluation_rows(records))
    df["Operational instruction"] = [decision_package(case)["operational"] for case in cases]
    df["Customer communication"] = [decision_package(case)["customer"] for case in cases]
    df["Supervisor review"] = [decision_package(case)["supervisor"] for case in cases]
    a,b=st.columns([1.05,.95],gap="large")
    with a:
        st.bar_chart(df.set_index("Shipment")[["Latency (s)"]],height=300,color="#ED6848")
        st.caption("Measured end-to-end case latency in the original run. This does not reflect chapter-by-chapter replay duration.")
    with b:
        st.markdown("#### Look beyond the average")
        st.write("**SHP-003 — 32.65s:** One Critic revision and an additional structured-output validation retry.")
        st.write("**SHP-004 — 28.58s:** Two resolution revisions triggered the configured limit and human escalation.")
        st.write("**SHP-001 / SHP-010 — 0.02s / 0.03s:** Routine events took the deterministic fast path without LLM reasoning.")
        st.write(f"**Exception-only mean — {mean_exception_seconds:.2f}s:** A clearer indicator of how long the agentic path took on these eight test cases.")
    st.dataframe(df,hide_index=True,use_container_width=True)
    st.download_button("Export the benchmark table",df.to_csv(index=False).encode("utf-8"),"delivery_exception_benchmark.csv","text/csv")
    heading("03 / INTERPRETATION", "What remains to be proved")
    cols=st.columns(3)
    for col,item in zip(cols,[
        ("01", "Operational baseline", "No measured manual-resolution comparison was supplied. Do not represent the notebook latency as demonstrated time savings."),
        ("02", "Scale & resilience", "Ten curated scenarios cannot establish reliability under production feeds, concurrent loads, distribution shifts or tool outages."),
        ("03", "End-to-end execution", "The proof of concept drafts decisions and communications; it does not confirm real replacements, dispatch changes or delivered customer notifications.")
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
st.markdown('<div class="footer-note"><strong>EXCEPTION / CONTROL</strong> &nbsp; · &nbsp; Completed multi-agent AI proof of concept &nbsp; / &nbsp; Recorded evidence replay. No live model, external API, real customer action or private playbook content is hosted in this presentation.</div>',unsafe_allow_html=True)
