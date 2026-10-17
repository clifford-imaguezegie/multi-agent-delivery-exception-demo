# Exception / Control — Delivery Exception Multi-Agent AI

**Public replay v2.3.4 | 17 October 2026 captured executions**

An interactive, read-only Streamlit portfolio demonstration of a previously executed multi-agent workflow for parcel-delivery exceptions. The demo displays **recorded** LangSmith events and the corresponding **executed notebook's** benchmark assessments. It makes no LLM calls and cannot change shipment state or send customer messages.

## What changed in v2.3.4

The application **retains exactly the same six workspaces, design, navigation and architecture** as v2.3.3. Only the run-specific data, descriptions, result evidence, playback reading speed, and release identifier have been refreshed.

- Imported all ten scenarios from `delivery_exception_all_langsmith_traces_PRIVATE (3).zip`, with final decisions from recorded `finalize` stages, intermediate Critic rationales, proposal/draft revisions, tool names, measured stage durations and start offsets. The **raw/private archive is not shipped**.
- Linked the current notebook's *individual assessment outputs* to their matching shipment IDs, cross-checking notebook revision counts and latencies with this trace batch. All ten scenarios have passing applicable benchmark checks. LLM-as-a-Judge coherence: 5/5 for eight cases, **3/5 for SHP-004**, and **2/5 for SHP-005** (mean 4.5/5). These are curated proof-of-concept assessments, not independently verified production outcomes.
- Corrected **SHP-003**: RESCHEDULE, no human escalation, Resolution Critic ACCEPT, ~14.53-second trace. **SHP-004** now has two resolution revision requests; SHP-008 has REVISE → ACCEPT; SHP-006 retains REVISE → ACCEPT. Case Stories, Agent Flow, Results, and the walkthrough's caption now agree with this batch.
- **Quick overview remains default (6–25 seconds per event)**. Comfortable is now **30–120 seconds**, and Extra reading time **60–240 seconds** to allow detailed review. Manual, Play, Pause, Back, Next and Reset remain. Playback time is intentionally separate from actual recorded execution time.
- The release footer identifies **v2.3.4**.
- Two *recovered* model/structured-output validation-error spans are present in SHP-004's private trace. The final workflow and notebook test passed; the public app reports the error count without exposing the raw error payload. Do not describe the run as error-free.

## Verified results for this trace batch

| Shipment | Recorded resolution | Supervisor escalation requested | Resolution Critic sequence | Root duration | Judge coherence |
| --- | --- | --- | --- | ---: | ---: |
| SHP-001 | N/A (routine) | No | No AI calls | 0.015s | 5/5 |
| SHP-002 | RESCHEDULE | Yes | ACCEPT | 17.466s | 5/5 |
| SHP-003 | RESCHEDULE | **No** | ACCEPT | 14.531s | 5/5 |
| SHP-004 | REPLACE | Yes | REVISE → REVISE | 29.041s | 3/5 |
| SHP-005 | REROUTE_TO_LOCKER | Yes | ACCEPT | 24.435s | 2/5 |
| SHP-006 | RETURN_TO_SENDER | **No** | REVISE → ACCEPT | 49.691s | 5/5 |
| SHP-007 | REPLACE | Yes | ACCEPT | 21.743s | 5/5 |
| SHP-008 | RESCHEDULE | Yes | REVISE → ACCEPT | 32.800s | 5/5 |
| SHP-009 | REPLACE | Yes | ACCEPT | 20.435s | 5/5 |
| SHP-010 | N/A (routine) | No | No AI calls | 0.041s | 5/5 |

**Aggregate:** 446 spans, 10 completed root traces, **21.02 seconds mean across ten cases**, **26.27 seconds across eight exceptions**; six cases requested supervisor escalation, two nonroutine exceptions did not, and two routine events bypassed AI. All ten cases passed their applicable Task, Exception, Resolution, Escalation, Tone and Tools checks in the executed notebook (tone/escalation are N/A for routine cases). No customer messages or delivery actions were executed.

SHP-001/010 can be flagged `partial` in the **private export manifests** because the trace exporter expected agent spans for every scenario; their deterministic fast-path root traces are valid. Do not confuse export warnings with failed operational executions.

## Workspaces (unchanged)

1. **The challenge:** Last-mile exception problem and measured result context.
2. **Architecture:** Original implemented LangGraph graph, deterministic fast path, RAG, tools, specialised agents, Critics and escalation.
3. **Case stories:** Ten guided evidence-grounded stories plus the 28-second edited SHP-006 walkthrough film (rebuilt with the current 49.69s execution label).
4. **Agent flow:** Seven-node animated replay with original stage ordering, revised reading pace, Critic feedback and measured stage times.
5. **Evidence room:** Per-stage proposals, objections, approved/rejected drafts, operational outcomes, tool identifiers and visibility boundaries.
6. **Results:** Root and stage timing, final outcomes, current-run benchmark checks, Judge coherence scores and internal recovered-error disclosure.

**Evidence boundary:** The LangSmith trace includes agent and tool inputs/outputs, which may contain confidential data. The bundled JSON is an allowlisted and automatically redacted extraction. Policy passages, raw spans and customer databases are not published. Human review remains necessary before making the source repository public.

## Deploy

Tested structurally on Python 3.13; Python 3.10+ is supported by the declared packages, subject to normal Streamlit compatibility. From the repository root:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

No API key or server API is required. `app.py` is the Streamlit entry point. The package includes `app.py`, supporting `.py` modules, `.streamlit/config.toml`, `data/recorded_cases.json` and `assets/shp006_story.mp4`. This build has offline automated validation; **a live deployed Streamlit browser check is still required**.

Run offline tests with:

```bash
python -m pytest -q
```

The demo must not be mistaken for a deployed logistics control system. Its latency cannot establish savings versus manual operation, and Judge coherence is not a substitute for operational correctness or independent human review. Critic ACCEPT is not supervisor approval.

## Private authoring workflow

The bundled `scripts/build_public_trace_replay.py` is an *offline* trace extraction utility and is not called by Streamlit. The app's JSON also contains allowlisted notebook benchmark outputs verified against this same trace batch. To regenerate the published JSON from private source materials, rebuild it in a **private working directory**, reconcile with the executed notebook assessments, run the regression suite and complete the `PUBLICATION_CHECKLIST.md` before publishing. Never upload private LangSmith archives, the original notebook, databases, internal playbooks, API credentials, or raw evaluation dumps to GitHub.
