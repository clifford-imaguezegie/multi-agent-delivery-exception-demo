# Exception / Control — Multi-Agent Delivery AI

**V2.3.1 | Readable Agent Flow replay + footer version | October 2026**

A public-facing, read-only Streamlit portfolio demonstration of the user-developed multi-agent last-mile delivery exception proof of concept. V2.3 retains the established plum/coral/cream visual design and six workspaces, while replacing the *earlier recorded experiment* with the new **17 October 2026 LangSmith rerun**.

> **Recorded replay — not live inference.** Streamlit reads a narrowly allowlisted JSON file. It does not call LLMs, LangSmith, operational APIs, customer databases, RAG services, or send any notifications.

## V2.3.1 usability refinements

- **Human-readable replay is now the default.** The original auto-advance rate was 1.15 seconds/event; the revised Agent Flow uses a word-count-adjusted reading window (typically 12–52 seconds per event at Comfortable pace). Longer Critic rationales receive more time. Visitors can select Extra reading time, Quick overview, or Manual step-by-step, and can Play/Pause/Back/Next/Reset as before. Leaving the browser tab pauses playback so decisions are not skipped.
- **Separation of time concepts:** The playback speed and reading countdown are for presentation only. Recorded LangSmith end-to-end and per-node timings are unchanged.
- **Explicit footer release:** Every workspace now finishes with **APP VERSION v2.3.1** and **TRACE · 17 October 2026**, making it simple to verify the correct deployment.
- **Scope:** No modifications to the captured traces, scenario outcomes, underlying agent logic, benchmark metrics, architecture, story chapters, or SHP-006 video.

## V2.3 evidence integration (preserved)

- **Intermediate Critic evidence:** Each observed Critic verdict displays its captured rationale, the proposal or unsent customer draft it reviewed, and the associated stage duration. For SHP-006, inspect the original REVISE objection, the revised proposal and subsequent ACCEPT.
- **Measured node timing:** LangSmith stage start and end timestamps are used to show real measured **node elapsed durations and start offsets** in the Agent Flow. These are wall-clock spans (which may contain subcalls); do not add their nested children to stage durations. The moving indicator is still an illustrative animation.
- **Run-specific fidelity:** The former SHP-004 two-revision storyline is **not carried forward**; its new run has Resolution Critic ACCEPT with separate required human escalation. SHP-003 now has two REVISE decisions and a terminal ESCALATE. SHP-007 includes Communication Critic ESCALATE.
- **Updated results:** The ten captured root spans have a **16.41-second mean**, while eight actionable exceptions average **20.51 seconds**. All ten runs have root and per-stage evidence; 428 total LangSmith spans were exported. SHP-001 and SHP-010 are intentionally routine fast-path cases.
- **Recorded-story video:** Replaced the archival SHP-004 explainer with a 28-second, silent, captioned **SHP-006 REVISE → ACCEPT** reconstruction based on the new trace. Its film duration is not the model inference time.
- **Honest evaluation boundaries:** Prior experimental completion, tool correctness and LLM coherence scores are **not represented as scores on this rerun**. New scoring requires evaluation output from the new execution.
- **Public data safety:** Only fields relevant to the replay and short agent outputs are exported. Customer and address redaction is applied; no raw LangSmith traces, private playbook passages, prompts, authentication tokens, retrieved context, or complete input/output states are packaged.

## Workspaces

1. **The challenge:** Operational problem, coordination approach and current run's measured timings.
2. **Architecture:** Original implemented LangGraph, deterministic fast path, tools/RAG, specialist agents, Critics, human escalation and LangSmith observability.
3. **Case stories:** Ten guided stories plus associated source-stage chronology and the updated SHP-006 walkthrough film.
4. **Agent flow:** Seven-node animated trace player with reading-paced auto-advance (Comfortable / Extra time / Quick overview), Manual mode, Back / Next / Play / Pause / Reset, measured stage timings and recovered Critic rationales.
5. **Evidence room:** Final resolution package, all Critic iterations and prior proposals, public-safe tool span names/durations, redacted unsent customer communication and governance notices.
6. **Results:** Current captured trace duration and outcomes, without presenting legacy evaluator scores as new-run validation.

## What the trace actually contains

| Case | Resolution review events | Latest run duration |
| --- | --- | ---: |
| SHP-001 | Routine fast path | 0.017s |
| SHP-002 | ACCEPT | 17.027s |
| SHP-003 | REVISE → REVISE, terminal ESCALATE | 39.522s |
| SHP-004 | ACCEPT (supervisor escalation separately required) | 16.337s |
| SHP-005 | ACCEPT (locker holding instruction preserved) | 16.548s |
| SHP-006 | REVISE → ACCEPT | 12.737s |
| SHP-007 | ACCEPT; Communication Critic ESCALATE | 28.832s |
| SHP-008 | ACCEPT | 21.070s |
| SHP-009 | ACCEPT | 12.013s |
| SHP-010 | Routine fast path | 0.018s |

**Important:** A Critic's ACCEPT is evidence of a recorded model assessment, not proof of operational correctness, customer approval or a completed delivery action. Although the new LangSmith trace includes individual stage timings, it does not establish speedups over manual operations.

## Setup and deployment

Python 3.10+ recommended, and Streamlit Community Cloud is a suitable host. Execute:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

No secrets or network access are needed for the **application** after installation.

To deploy, create or update the public GitHub repository (e.g. `multi-agent-delivery-exception-ai`). Put `app.py` in the root with its modules, `.streamlit/`, `data/` and `assets/`. On Streamlit Community Cloud select `app.py` as the entry point.

**Do not upload:** the private LangSmith ZIP, the original notebook, private CSV/SQLite files, internal policy PDF, customer information, or API credentials. The `scripts/build_public_trace_replay.py` utility takes a **private local ZIP** and writes only explicitly allowlisted values. It is an authoring utility, *not* used by the public Streamlit application. Never point the deployed app at a private trace export.

**Privacy gate:** Automated redaction does not guarantee that every name, address, contractual term, or internal policy paraphrase has been caught. A human must inspect `data/recorded_cases.json`, particularly each `rationale` and `communication_message`, before making the repository public. If internal policy content is uncertain, remove the passage rather than publish it.

## Repository structure

```text
app.py                              Six-workspace Streamlit application
agent_flow.py                       Interactive recorded-stage graph
review_evidence.py                  Critic feedback + decision authority
storyline.py                        Narrative evidence chapters
decision_package.py                 Four-part outcome presentation
replay_data.py                      Dataset loader and validation
style.css                           Plum, coral and cream branding
.streamlit/config.toml              Streamlit visual theme
data/recorded_cases.json            Privacy-redacted, allowlisted LangSmith stages
assets/shp006_story.mp4             Current-run edited walkthrough
scripts/build_public_trace_replay.py Private authoring from LangSmith ZIP (optional)
scripts/build_walkthrough_video.py   Offline edited-video authoring
tests/                              Offline integrity, replay and privacy checks
```

## Integrity checks

```bash
python -m pytest -q
python -m py_compile app.py agent_flow.py review_evidence.py storyline.py replay_data.py
```

A production/hosted browser review remains essential. In particular, verify the header on mobile and desktop, Agent Flow reading pauses and Manual mode, footer version label, node movement, exact Critic review text, redactions, video playback and the public case JSON download.

**Data provenance:** Private file `delivery_exception_all_langsmith_traces_PRIVATE.zip`, 10 case folders, each with trace, events and manifest. The public dataset contains only a selected subset from this execution, not the original raw traces. SHP-001/010 may have been labelled `partial` by the old exporter because it incorrectly expected AI-agent spans for intentionally filtered routine events; their captured deterministic paths are complete.
