# Delivery Exception AI — Recorded Execution Replay

**Portfolio demonstration | Read-only Streamlit application | October 2026**

This application presents a completed educational multi-agent AI proof of concept through **ten original, saved benchmark executions**. It does **not** run LangGraph, call LLMs, retrieve the private playbook, send customer messages, or manipulate real shipments.

## What visitors can explore

- **Overview:** business problem, agent architecture and benchmark highlights.
- **Scenario Replay:** choose among SHP-001 to SHP-010; reveal the saved workflow trajectory one step at a time using **Next**, **Previous**, **Reset** and **Show all**. Final output and ground-truth comparison are visible alongside the replay.
- **Engineering Evidence:** recorded Resolution Agent and Critic outputs; rule-engine signals; agent/tool invocation logs; source chunk/page references; anonymised customer-communication drafts.
- **Evaluation:** aggregate metrics, denominators, per-case outcomes, recorded elapsed time, and a CSV download.

### Suggested guided tour

1. Start with **SHP-003** — reschedule with one revision before the Critic accepts.
2. Inspect **SHP-004** — repeated resolution revisions, revision ceiling, and escalation.
3. Explore **SHP-005** — third attempt, locker-availability constraints and escalation.
4. Compare **SHP-001** and **SHP-010** — routine/noise filtering without LLM agent calls.
5. Finish on **Evaluation**, where each outcome is compared with its source benchmark label.

## Local quick start

Requires Python 3.10 or later.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit will display the local URL (typically `http://localhost:8501`). No API key or external data source is required. The complete replay dataset is already under `data/recorded_cases.json`.

## Deployment (optional)

1. Place the content of this folder in a **public GitHub repository**, keeping the same paths. Only include this sanitised package; **do not push the original notebook or original data files**.
2. In Streamlit Community Cloud, create an app from your repository.
3. Set the main file path to `app.py`; Streamlit installs dependencies from `requirements.txt`.
4. Open the hosted app and verify the ten selectable scenarios and replay controls before sharing its URL on Great Learning or LinkedIn.
5. Keep the banner **Recorded execution replay, not live processing** prominent on the deployed site.

For other hosts, execute `streamlit run app.py --server.address 0.0.0.0 --server.port ${PORT:-8501}` as the startup command.

## Recorded source and reproducibility

- **Source:** `Delivery_Exception_Multi_Agent_AI_Solution_Full_Code_Markdown_Aligned(3).ipynb` (not included in the public package).
- **Extraction:** `scripts/extract_notebook.py` reads saved notebook output cells 306, 309, 312, 315, 318, 321, 324, 327, 330, and 333. The package contains original final actions, scenario assessments, saved trajectory lines, Critic summaries, tools used, and limited policy reference metadata.
- **Privacy:** customer names, customer IDs, addresses, and some account details were redacted. The original playbook is labelled **Internal Use Only**, so the public dataset exports retrieved page numbers and chunk IDs, not its full text. The notebook itself and raw CSV, database, and PDF are not packaged.
- **Finalisation line:** the original trace includes a JSON object containing the customer message. For privacy, the replay substitutes a minimal finalisation event with the real recorded resolution, escalation flag, and revision count; the separate anonymised draft is retained for inspection.
- **Authenticity:** the ordering of steps is preserved, but there are **no per-step timestamps**. The app does not fabricate node-level latencies; only the original case-level elapsed time is shown. A step is revealed on demand rather than delayed to imitate computation.
- **Benchmark:** 10 curated cases. Reported task completion 10/10; tool-call correctness 10/10; **escalation accuracy 8/8** (two routine events excluded); **escalation routing 10/10**; mean LLM-judge coherence 5/5; reported mean latency 13.86 seconds. Small curated test performance must not be interpreted as generalisable production accuracy.
- **Exceptions:** SHP-004's Critic summary shows a forced ESCALATE after reaching the revision limit; its intermediate REVISE events are captured by trajectory entries. The notebook doesn't provide versioned full text of every intermediate Critic payload, so the app doesn't invent any.

To re-extract from the user's private notebook, without including that notebook in the public repository:

```bash
python scripts/extract_notebook.py "path/to/Delivery_Exception_Multi_Agent_AI_Solution_Full_Code_Markdown_Aligned(3).ipynb"
```

Run basic integrity and privacy regression tests:

```bash
python -m pytest -q
```

## Scope and limitations

This is an **educational proof-of-concept portfolio replay**, not a logistics operating system or a live autonomous agent demonstration. The execution records were generated previously in a notebook. The UI is not connected to real carriers, supervisors, customer contacts or production systems; it cannot dispatch a driver, trigger a refund, issue a replacement, or send an email. No new AI inference occurs during playback. Runtime version compatibility and hosting are subject to verification in the intended target environment.

## Repository contents

```text
app.py                         Streamlit front end
replay_data.py                 Data loader and validation
requirements.txt               Python dependencies
.streamlit/config.toml         Visual theme
 data/recorded_cases.json       Anonymised recorded evidence
 scripts/extract_notebook.py   Re-extract from private notebook
 tests/test_recorded_data.py   Integrity and privacy tests
```
