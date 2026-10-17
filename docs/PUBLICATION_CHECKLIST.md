# Release V2.4.0 — operational value presentation update

- [ ] On **The challenge**, confirm five distinct Operational Value cards are visible and readable on desktop and mobile.
- [ ] Confirm the proof-of-concept evidence ribbon uses 26.27s (eight exception scenarios) and 10/10 applicable benchmark cases, **without claiming manual labour savings**.
- [ ] Verify the six existing workspaces and architecture remain unchanged and the footer displays **v2.4.0**.
- [ ] Confirm no customer actions or live model inference are implied; business gains are proposed for pilot validation.

# V2.3.4 — Public demonstration acceptance checklist

This is an **automatically redacted, allowlisted** evidence replay; redaction alone cannot guarantee that internal details or identities have been removed. Perform a final human review before publishing.

## Sensitive-content gate

- [ ] Read `data/recorded_cases.json`, especially nested `agent_events[*].proposal.rationale`, `agent_events[*].review.rationale`, `agent_events[*].draft.communication_message`, operational actions, and the final decision package.
- [ ] Check all scenario labels, customer fields, event notes, and escalation triggers for names, addresses, account references, contractual terms, or internal policy details.
- [ ] Confirm the public GitHub repository contains **no** private LangSmith ZIP, raw spans, exported traces, original executed notebook, private PDF playbook, customer/locker database, source CSV, API key, or `.env` file.
- [ ] The public application must not expose raw recoverable error payloads from SHP-004; show only their count and the fact that the run completed.

## Run/evidence consistency

- [ ] Footer shows `APP VERSION v2.3.4` on every workspace, with no raw CSS text above the header.
- [ ] The Challenge and Results show **21.02s** overall, **26.27s** exception-only, and **446** recorded spans.
- [ ] SHP-003 displays **RESCHEDULE**, **no supervisor escalation**, Resolution Critic **ACCEPT** and ~14.53s; no remnant of the previous failed run.
- [ ] SHP-004 shows two Resolution Critic revisions and escalated final outcome. SHP-006 and SHP-008 demonstrate REVISE → ACCEPT.
- [ ] Confirm SHP-005/007 Communication Critic escalation is distinguishable from resolution Critic decisions.
- [ ] The Results table correctly shows the executed notebook's benchmark PASS/N/A values and the Judge coherence scores (SHP-004 3/5, SHP-005 2/5).
- [ ] Root durations, individual node durations and **animated reading pauses** are labelled as different measures. Do not claim AI-to-manual speedup.
- [ ] SHP-006's 28s silent edited video now labels its **49.69-second actual captured root duration**, not its film duration.

## Usability

- [ ] Default Agent Flow mode is **Quick overview**, stepping after approximately **6–25s** per event.
- [ ] Comfortable holds each event for **30–120s**; Extra reading time holds **60–240s**. Test both with a long Critic rationale; verify Manual never advances automatically.
- [ ] Play, Pause, Back, Next, Reset, tab-switch pausing, event details and selected agent indicator all work as expected.
- [ ] Inspect header, footer, video player, tables and Agent Flow on desktop and mobile. Run a **full deployed Streamlit browser check** after GitHub redeployment.

## Interpret results correctly

- The ten selected scenarios form a **curated test set**, not a realistic escalation frequency or production acceptance benchmark.
- Six scenarios requested human escalation; this does not indicate any supervisor actually approved or executed an action.
- The private trace includes two **recovered** structured-output/model validation subspan errors in SHP-004; the final workflow and notebook assessment passed.
- The notebook Judge's coherence score measures reasoning coherence, **not** independent operational correctness or production readiness.
- Routine cases SHP-001 and SHP-010 intentionally bypassed agent inference even if their private export manifests say `partial` due to an overstrict span-count expectation.
