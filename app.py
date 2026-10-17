"""Delivery Exception Multi-Agent AI | Recorded evidence replay (read-only)."""
from __future__ import annotations
import json
from html import escape

import pandas as pd
import streamlit as st

from replay_data import load_data, evaluation_rows

st.set_page_config(page_title="Delivery Exception AI | Recorded Replay", page_icon="📦", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
.stApp {background: #F7F9FC; color: #162438;}
.block-container {padding-top: 1.8rem; max-width: 1320px;}
[data-testid="stSidebar"] {background: #EAF0F6;}
.hero {padding: 28px 32px; border-radius: 17px; background: linear-gradient(108deg,#101F38 0%,#244563 100%);color:#F7FCFF; margin-bottom: 17px;}
.hero h1 {font-size: 2.05rem;font-weight: 760; letter-spacing: -.03em; line-height: 1.13; margin: .2rem 0 .6rem; color:#fff;}
.hero p {font-size:1rem; color:#DCE7F3;margin:0;max-width:830px;}
.kicker {color:#7BD9D2;font-size:.82rem;font-weight: 700;letter-spacing:.12em;text-transform:uppercase;}
.notice {background:#E8F3F4;padding: 13px 17px;border-left:4px solid #148B93;border-radius:7px;color:#194C52;margin: 4px 0 20px; font-size:.92rem;}
.panel {border:1px solid #DDE7F0; background:white; border-radius:13px; padding:18px 20px; margin:6px 0 17px;}
.panel h3 {font-size:1.05rem;margin:0 0 .6rem;color:#193250;}
.pill {background:#E8F2F5;color:#116C7B;padding:4px 10px;border-radius:99px;font-weight:680;font-size:.8rem;}
.smallcaps {font-size: .75rem; color:#62748B;letter-spacing:.08em; font-weight: 720; text-transform:uppercase;}
.pathline {display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin: 14px 0 18px;}
.pathnode {border:1px solid #BDD5E8;background:#F4F9FC;border-radius:10px;padding:9px 14px;font-size:.87rem;font-weight:650;color:#214C68;}
.patharrow {font-weight:800;color:#537D94;}
.stepdone {color:#0B756B;}
div[data-testid="stMetric"] {background:#FFF;border:1px solid #DCE6F0;border-radius:11px;padding:13px 16px;}
footer {visibility:hidden;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_data

def data():
    return load_data()

records = data()
cases = records["cases"]
case_lookup = {c["id"]:c for c in cases}


def tag(text: str):
    return f'<span class="pill">{escape(str(text))}</span>'


def hero(title: str, detail: str, category="ENGINEERING PORTFOLIO · RECORDED EVIDENCE"):
    st.markdown(f'<div class="hero"><div class="kicker">{escape(category)}</div><h1>{escape(title)}</h1><p>{escape(detail)}</p></div>', unsafe_allow_html=True)


def notice():
    st.markdown('<div class="notice"><b>Recorded execution replay, not live processing.</b> All decisions, steps and metrics come from the stored course-project notebook. Playback reveals captured steps in order; it does not re-run agents, call APIs, or perform real delivery actions. Names and direct identifiers are redacted.</div>',unsafe_allow_html=True)


def metric_strip():
    a=records["aggregate"]
    cols=st.columns(4)
    cols[0].metric("Benchmark scenarios",a["cases"])
    cols[1].metric("Task completion",f'{a["task_completion_percent"]:.0f}%')
    cols[2].metric("Mean coherence",f'{a["mean_coherence_out_of_5"]:g}/5')
    cols[3].metric("Mean run latency",f'{a["mean_latency_seconds"]:.2f} s')
    st.caption("10 curated notebook test cases · Evaluator-reported metrics; not production performance")


def overview():
    hero("Multi-Agent Delivery Exception Management", "A working engineering proof of concept presented through ten authentic, previously recorded LangGraph executions.")
    notice()
    metric_strip()
    st.subheader("From event detection to accountable resolution")
    st.markdown('''<div class="pathline"><span class="pathnode">Delivery event + customer context</span><span class="patharrow">→</span><span class="pathnode">Preprocessor & guardrails</span><span class="patharrow">→</span><span class="pathnode">Resolution agent</span><span class="patharrow">→</span><span class="pathnode">Independent Critic</span><span class="patharrow">→</span><span class="pathnode">Communication + Critic</span><span class="patharrow">→</span><span class="pathnode">Decision or escalation</span></div>''',unsafe_allow_html=True)
    a,b=st.columns(2, gap="large")
    with a:
        st.markdown("#### Business challenge")
        st.write("Last-mile deliveries create exceptions requiring a decision: failed attempts, address mismatches, refusal, package damage, or weather disruption. This project explores how coordinated agents and deterministic rules can assist human operations teams.")
        st.markdown("#### What was implemented")
        st.write("LangGraph orchestration; LLM resolution and communication agents; separate Critic reviews; playbook retrieval; customer and locker lookup tools; escalation logic; final decision assembly; and benchmark evaluation with traceability.")
    with b:
        st.markdown("#### Representative engineering cases")
        st.write("**SHP-003:** One resolution revision before acceptance.")
        st.write("**SHP-004:** Two revisions reach the configured limit, forcing escalation.")
        st.write("**SHP-005:** Third failed attempt with locker constraints and mandatory escalation.")
        st.write("**SHP-001 & SHP-010:** Routine non-exceptions filtered without calling the LLM agents.")
    st.info("Use Scenario Replay to step through the actual recorded decision path, then Engineering Evidence to inspect validation, tool calls, and retrieval references.")


def step_role(step: str) -> str:
    role=step.split(":", 1)[0].strip()
    return {"preprocessor":"Preprocessor", "orchestrator":"Orchestrator", "resolution_agent":"Resolution Agent",
            "critic_resolution":"Resolution Critic", "communication_agent":"Communication Agent",
            "critic_communication":"Communication Critic", "finalize":"Finalisation"}.get(role, "Workflow")


def outcome_panel(c: dict):
    f=c["final_action"]
    st.markdown("#### Recorded final outcome")
    st.markdown(tag("EXCEPTION" if f["is_exception"]=="YES" else "ROUTINE EVENT")+" "+tag("ESCALATED" if f["escalated"] else "NOT ESCALATED"),unsafe_allow_html=True)
    st.write("**Resolution:**",f["resolution"] or "N/A")
    st.write("**Communication tone:**", f["tone"] or "N/A")
    st.write("**Resolution revisions:**", f["revision_count"])
    st.write("**Guardrail blocked:**", "Yes" if f["guardrail_blocked"] else "No")
    st.write("**Recorded latency:**",f'{c["metrics"]["latency_seconds"]:.2f} s')
    st.caption("End-to-end latency from original execution; playback speed does not represent model timing.")
    st.markdown("#### Ground truth comparison")
    gt=c["ground_truth"]
    st.table(pd.DataFrame([
        {"Check":"Exception", "Predicted":f["is_exception"], "Ground truth":gt["exception"]},
        {"Check":"Resolution", "Predicted":f["resolution"], "Ground truth":gt["resolution"]},
        {"Check":"Escalation", "Predicted":"YES" if f["escalated"] else "NO", "Ground truth":gt["escalation"]},
        {"Check":"Tone", "Predicted":f["tone"], "Ground truth":gt["tone"]},
    ]).set_index("Check"))


def replay(c: dict):
    hero("Scenario Execution Replay", "Step through the original workflow trajectory, then inspect the recorded decision and assurance evidence.","CAPTURED WORKFLOW · NO LIVE API CALLS")
    notice()
    f=c["final_action"]
    st.subheader(f'{c["id"]} — {c["title"]}')
    st.caption("Source: captured notebook stream output; ordered agent and orchestrator events, not per-node timestamps")
    event, customer=c["event"],c["customer"]
    with st.expander("Operational input and customer context", expanded=True):
        a,b=st.columns(2)
        with a:
            st.write("**Status:**",event.get("status_code","—"))
            st.write("**Event:**",event.get("status_description","—"))
            st.write("**Delivery attempts:**",event.get("attempt_number","—"))
            st.write("**Package:**",f'{event.get("package_type","—")} · {event.get("package_size","—")}')
            if event.get("prior_attempt_notes"):
                st.write("**Prior attempt notes:**", "; ".join(event["prior_attempt_notes"]))
        with b:
            st.write("**Customer tier:**",customer.get("tier","—"))
            st.write("**Preferred channel:**",customer.get("preferred_channel","—"))
            st.write("**Exceptions in last 90 days:**",customer.get("exceptions_last_90d","—"))
            if c["escalation_signals"].get("triggers"):
                st.write("**Escalation signal(s):**")
                for t in c["escalation_signals"]["triggers"]:st.write("• "+t)
    key="replay_pos_"+c["id"]
    st.session_state.setdefault(key,0)
    steps=c["trajectory"]
    pos=max(0,min(st.session_state[key],len(steps)))
    st.markdown("#### Playback controls")
    col0,col1,col2,col3=st.columns([1,1,1,1])
    with col0:
        if st.button("↺ Reset",use_container_width=True):st.session_state[key]=0;st.rerun()
    with col1:
        if st.button("← Previous",disabled=pos==0,use_container_width=True):st.session_state[key]=pos-1;st.rerun()
    with col2:
        if st.button("Next →",disabled=pos==len(steps),type="primary",use_container_width=True):st.session_state[key]=pos+1;st.rerun()
    with col3:
        if st.button("Show all",disabled=pos==len(steps),use_container_width=True):st.session_state[key]=len(steps);st.rerun()
    pos=st.session_state[key]
    st.progress(pos/len(steps),text=f"{pos} of {len(steps)} captured workflow events revealed")
    left,right=st.columns([1.13,0.87],gap="large")
    with left:
        if pos==0:
            st.info("Select **Next →** to reveal the original execution path, one recorded event at a time.")
        else:
            current=steps[pos-1]
            st.markdown('<div class="smallcaps">Current recorded event</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="panel"><h3>{escape(step_role(current))}</h3>{escape(current)}</div>',unsafe_allow_html=True)
        with st.container(height=430,border=True):
            for i,line in enumerate(steps[:pos]):
                st.markdown(f"**{i+1:02d}. {step_role(line)}**")
                st.caption(line)
            if pos==0:
                st.caption("Recorded events will appear here as you advance.")
    with right:
        outcome_panel(c)
    if pos==len(steps):st.success("Replay complete. All displayed events are from the saved execution record.")


def evidence(c: dict):
    hero("Engineering Evidence", "Inspect the actual recorded agent outputs, validation findings, tool invocations, and playbook reference metadata.")
    notice()
    st.subheader(f'{c["id"]} — {c["title"]}')
    t1,t2,t3,t4=st.tabs(["Agent decisions", "Tools & guardrails", "Playbook provenance", "Customer draft"])
    with t1:
        res=c["resolution_agent"]; rc=c["resolution_critic"]; cm=c["communication_critic"]
        st.markdown("#### Resolution Agent")
        st.write("**Decision:**",res.get("resolution") or "N/A")
        if res.get("operational_action"):st.write("**Operational action:**",res["operational_action"])
        st.write(res.get("rationale") or "No LLM resolution invoked; routine event filtered by deterministic preprocessing.")
        st.markdown("#### Independent Resolution Critic")
        st.write("**Recorded final critic outcome:**",rc.get("decision") or "Not invoked")
        st.write(rc.get("rationale") or "No Critic invocation for a routine event.")
        st.caption("Intermediate REVISE outcomes are shown in the workflow trajectory. The notebook's summary captures the final Critic result, not a full versioned Critic payload per iteration.")
        st.markdown("#### Communication Critic")
        st.write("**Decision:**",cm.get("decision") or "Not invoked")
        st.write(cm.get("rationale") or "No customer communication required.")
    with t2:
        st.markdown("#### Captured tool and agent calls")
        if c["tool_calls"]:
            for i,v in enumerate(c["tool_calls"],1):st.write(f"{i}. `{v}`")
        else:st.info("No tool invocations captured.")
        st.markdown("#### Escalation and guardrails")
        esc=c["escalation_signals"]
        st.write("**Escalation triggers:**", "; ".join(esc.get("triggers",[])) or "None")
        st.write("**Resolution constraints:**", "; ".join(esc.get("resolution_constraints",[])) or "None")
        st.write("**Operational constraints:**", "; ".join(esc.get("operational_constraints",[])) or "None")
        st.write("**Guardrail blocked:**", "Yes" if c["final_action"].get("guardrail_blocked") else "No")
        st.write("**Revision count:**",c["final_action"].get("revision_count",0))
    with t3:
        st.markdown("#### Source references, not internal playbook text")
        refs=c["playbook_references"]
        if refs:
            st.dataframe(pd.DataFrame(refs).rename(columns={"page":"Source page", "chunk_id":"Retrieved chunk ID"}),hide_index=True,use_container_width=True)
        else:st.info("No playbook context retrieved for this routine event.")
        st.caption("The notebook labels its playbook 'Internal Use Only'. This portfolio demo preserves chunk/page provenance but withholds the policy passages. References alone do not make the original PDF publicly accessible.")
    with t4:
        comm=c["communication_agent"]
        if comm.get("communication_message"):
            st.markdown("#### Recorded draft · recipient anonymised")
            st.write("**Tone:**",comm.get("tone_label") or "Not specified")
            st.text(comm["communication_message"])
            st.caption("This is a redacted historical agent draft. It was not sent to a customer, and the UI performs no outbound messaging.")
        else:st.info("No customer message needed. The deterministic preprocessor filtered this routine event.")
    st.download_button("Download anonymised case evidence (.json)",data=json.dumps(c,indent=2,ensure_ascii=False),file_name=f"{c['id']}_recorded_evidence.json",mime="application/json")


def evaluation():
    hero("Benchmark Evaluation", "A transparent view of the ten course-project test cases, including evaluation coverage and recorded execution times.")
    notice()
    metric_strip()
    st.markdown("#### Benchmark metrics and denominator")
    ag=records["aggregate"]
    a,b,c=st.columns(3)
    a.metric("Tool-call accuracy",f'{ag["tool_call_percent"]:.0f}%','10 / 10 evaluated',delta_color="off")
    b.metric("Escalation accuracy",f'{ag["escalation_accuracy_percent"]:.0f}%','8 / 8 explicit labels',delta_color="off")
    c.metric("Escalation routing",f'{ag["escalation_routing_percent"]:.0f}%','10 / 10 incl. 2 routine cases',delta_color="off")
    st.caption("Coherence was assigned by an LLM-as-a-Judge, not independently audited against a production dataset. The original notebook reports 5/5 on all ten scenarios.")
    st.markdown("#### Shipment-level outcomes")
    rows=evaluation_rows(records)
    frame=pd.DataFrame(rows)
    st.dataframe(frame,hide_index=True,use_container_width=True)
    csv=frame.to_csv(index=False).encode("utf-8")
    st.download_button("Download benchmark table (CSV)",csv,"benchmark_evaluation.csv","text/csv")
    st.markdown("#### Recorded case latency (seconds)")
    st.bar_chart(frame.set_index("Shipment")[["Latency (s)"]],height=265)
    st.markdown("#### Limits of this evidence")
    st.write("These are 10 curated, educational benchmark scenarios. Results do not measure accuracy under real-world traffic, distribution shift, security attacks, SLA variability, or large-scale concurrent usage. Only original overall run latency is available; individual node durations were not recorded in the output being replayed. No claims of live operations or production deployment are made.")


with st.sidebar:
    st.markdown("## 📦 Exception AI")
    st.caption("Engineering project · recorded evidence")
    st.divider()
    page=st.radio("Workspace",["Overview","Scenario Replay","Engineering Evidence","Evaluation"],index=0)
    st.divider()
    sid=st.selectbox("Scenario",options=list(case_lookup),format_func=lambda s:f"{s} · {case_lookup[s]['title']}",index=3)
    selected=case_lookup[sid]
    st.caption("Choose any recorded shipment scenario. The selection is shared across the replay and evidence pages.")
    st.divider()
    st.caption("READ-ONLY · NO LIVE MODEL · NO APIs · NO CUSTOMER ACTIONS")
    st.caption("Based on completed multi-agent AI coursework and saved notebook outputs.")

if page=="Overview":overview()
elif page=="Scenario Replay":replay(selected)
elif page=="Engineering Evidence":evidence(selected)
else:evaluation()
