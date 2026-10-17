# Exception / Control — Multi-Agent Delivery AI

**Version 2.1 — Decision-package and animated-agent-flow update | October 2026**

A public portfolio presentation of the completed **multi-agent last-mile delivery exception handling** proof of concept. This release has its own plum/coral/cream visual identity, six focused workspaces, a notebook-grounded architecture map, chapter-based storytelling, a 36-second silent captioned walkthrough, and an interactive animated replay of the original recorded agent transitions.

> **Important:** This is a **recorded replay**, not live execution. The Streamlit application never runs the original agents, calls OpenRouter, retrieves the private playbook, reads customer databases, sends messages, or changes real shipments.

## The business problem

When last-mile deliveries fail, human operations teams must triage noisy status feeds, examine context from driver notes and customers, consult operational policy, decide whether to reschedule, reroute, replace or return the shipment, identify supervisor escalation requirements, and draft communications. The original proof of concept explores how deterministic controls plus coordinated LLM agents could streamline and improve consistency of these decisions.

## Six visitor workspaces

1. **The challenge:** Plain-English operational problem, the solution approach and responsibly labelled benchmark outcomes.
2. **Architecture:** Data/knowledge inputs → deterministic preprocessor → LangGraph orchestrator → operational tools and RAG → Resolution Agent / independent Critic with capped revision loop → Communication Agent / Critic → policy escalation and finalisation, with LangSmith observability. Also identifies the two Gemma model roles.
3. **Case stories:** Every one of the ten shipments has evidence-grounded, plain-English story chapters, independent navigation, chapter evidence, **full decision packages**, and the full original-order recorded event sequence. Includes a **36-second captioned MP4** on the damaged fragile VIP shipment SHP-004.
4. **Agent flow (new):** An interactive seven-node architecture with a moving indicator that follows **every captured trace event in its original order**. Use Play/Pause, Next/Back, Reset and replay speed. Displays the current agent's captured output alongside the latest events and overall measured case latency. Critic revision loops and supervisor escalation occur exactly as recorded. The animation is **illustrative**, not a time-accurate inference recording; **individual agent durations were not captured**.
5. **Evidence room:** Anonymised recorded agent decisions, tools, Critic outcomes, safeguards, policy reference metadata, communication drafts and original execution event lines.
6. **Results:** Source benchmark metrics, per-case measured elapsed times, whole-sample versus exception-only mean latencies, a downloadable benchmark table (including primary resolution, operational instruction, communication and supervisor decision) and evidence limitations.

## V2.1 change log

- **Header visibility:** Increased Streamlit top spacing and strengthened brand text contrast to keep the header below the fixed Streamlit toolbar.
- **Full decision package:** Every selected case now displays **primary resolution**, **operational handling**, **customer-contact / draft status**, and **supervisor escalation**. These are deliberately distinct: for example **SHP-005** proposes rerouting to a locker, while the recorded operational instruction is **hold at depot pending supervisor** because the available locker is full. No delivery, outreach or escalation actually occurs in this read-only replay.
- **Animated agent trace:** New **Agent flow** workspace uses only the original saved event order, including repeated visits to agents, Critic REVISE loops, structured-output retries and routine-event fast paths. Replay pace is controlled by the visitor and is unrelated to actual measured case latency.
- **Existing design preserved:** The Challenge, Architecture, Case stories, Evidence room and Results remain available in the original plum/coral/cream editorial style.

## Key measured figures

| Measurement | Recorded result | Notes |
| --- | ---: | --- |
| All-run mean end-to-end latency | **13.86 seconds** | Across 10 cases including 2 non-exceptions |
| Exception-only mean latency | **17.32 seconds** | Eight actionable exception cases, calculated from individual stored times |
| Individual exception latency range | **8.41–32.65 seconds** | Cannot claim every exception finishes within 15 seconds |
| Non-exception fast path | **0.02 / 0.03 seconds** | Routine events: SHP-001, SHP-010 |
| Task completion | **10 / 10** | Small curated benchmark |
| Tool-call correctness | **10 / 10** | Small curated benchmark |
| Escalation accuracy | **8 / 8** | Cases with applicable escalation labels |
| Escalation routing correctness | **10 / 10** | Includes two routine/no-escalation cases |
| Coherence | **5 / 5** | Mean score from LLM-as-a-Judge in original notebook |

These results are **not evidence of measured improvement over manual exception handling**, nor a production reliability benchmark. No per-node timings are provided in the saved notebook event traces, so the guided chapters and animation never imply per-stage timings.

## Local quick start

Use **Python 3.10+**. The source file was syntax-checked with the available local Python runtime, but should be browser-tested in the selected Streamlit deployment environment.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Visit the local URL supplied by Streamlit (usually http://localhost:8501). No credentials or external APIs are needed. The app reads the included anonymised `data/recorded_cases.json`.

## Streamlit Community Cloud

1. Create a public GitHub repository for this **sanitised demo package only**. Do **not** upload the private original notebook, source CSVs, SQLite database, internal playbook PDF, customer data or credentials.
2. Upload `app.py`, `replay_data.py`, `storyline.py`, `agent_flow.py`, `decision_package.py`, `style.css`, `.streamlit/config.toml`, `requirements.txt`, `data/recorded_cases.json`, `assets/shp004_story.mp4`, and supporting scripts/tests.
3. Configure `app.py` as the main file in Streamlit Community Cloud.
4. Check header visibility, navigation, full four-part outcome cards, animated flow controls and loops, data table, story chapter buttons, scenario selection, provenance tabs, and embedded MP4 on the hosted site.
5. Share the URL alongside your LinkedIn and Great Learning portfolio entries, and label it **recorded execution replay**.

## Provenance, privacy and faithful replay

- **Source:** `Delivery_Exception_Multi_Agent_AI_Solution_Full_Code_Markdown_Aligned(3).ipynb` — the original, private course-project notebook.
- `scripts/extract_notebook.py` was used to build the redacted source dataset from ten stored execution records. It must be run privately if re-extracting; do not package the notebook itself in the public repo.
- `storyline.py` generates editorial chapter summaries exclusively from the captured scenario values and trajectories. All original exported event lines remain inspectable under **Case stories → Original chronological event sequence** and **Evidence room → Raw event history**.
- SHP-004's Critic requested **two revisions**, and the orchestrator **forced escalation** when the configured revision limit was reached. The video is a silent, edited reconstruction of this evidence; it is **not** a recording of original inference and its 36-second length must not be confused with the **28.58-second** original run.
- The original playbook is marked **Internal Use Only**. The public package includes chunk/page reference metadata, not full policy passages.
- Names, customer IDs, street addresses and other direct identifiers were redacted before export. Review any new data and assets for private information before publishing.
- The replay is not a live logistics operating system: it cannot dispatch a vehicle, replace a package, process a refund, send a customer message or contact a supervisor.
- The animated indicator follows logged nodes **in order**. Each displayed source trace line is unchanged from the anonymised source and is never assigned a fabricated node duration. The whole-case measured time is shown separately.
- For SHP-005, rerouting to a locker was a **resolution category**; the recorded operational instruction explicitly requires a supervisor hold, not an executed reroute.

## Repository structure

```text
app.py                         Six-page Streamlit application
style.css                      Distinct editorial plum/coral/cream design
storyline.py                   Evidence-grounded chapter summaries
agent_flow.py                  Interactive HTML/SVG playback generated from saved traces
decision_package.py           Full recorded resolution + handling + communication + escalation summaries
replay_data.py                 Original recorded-case loader and validators
.streamlit/config.toml         Native Streamlit theme
requirements.txt               Streamlit + pandas
assets/shp004_story.mp4        Silent, captioned, edited video reconstruction
data/recorded_cases.json       Sanitised original replay evidence
scripts/extract_notebook.py    Private notebook extraction helper
scripts/build_walkthrough_video.py  Offline authoring script; not needed by Streamlit
tests/                         Content, privacy, and story integrity checks
```

## Testing

```bash
python -m pytest -q
```

The offline authored video can be regenerated with Pillow and ffmpeg from the recorded SHP-004 record:

```bash
python scripts/build_walkthrough_video.py
```

A local/hosted browser acceptance pass should be completed before publicly sharing the deployment.
