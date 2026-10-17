# Pre-publication review

The application is intentionally read-only and does not embed or call live credentials. The JSON is an **automatically redacted, allowlisted** derivative of the private LangSmith ZIP, not an independently certified anonymisation.

Before uploading this package to a public GitHub repository:

- Read `data/recorded_cases.json`, especially `agent_events[*].proposal.rationale`, `agent_events[*].review.rationale`, `agent_events[*].draft.communication_message`, and final agent rationales. Remove any names, addresses, delivery identifiers (other than SHP-00x), or internal policy instructions you do not have permission to disclose.
- Review `customer` fields, case `event` summaries, and `escalation_signals.triggers` for business confidentiality.
- Confirm no private trace ZIP, original notebook, proprietary playbook, customer SQLite/CSV, API tokens, or private dashboard screenshots are present.
- View the Streamlit application on desktop and mobile, then play SHP-003, SHP-004, SHP-006 and SHP-007. Verify the timing panel, any revisions and the SHP-006 video.
- Keep the public heading **Recorded replay — not live inference** and do not present earlier benchmark evaluator scores as scores from the current rerun.

## Trace timing limitations

Recorded durations are elapsed times of LangGraph stages, and may include internal model or tool calls. They are **not independent latency benchmarks of underlying model calls**. Nested spans overlap with their parent stages and must not be summed to produce full case latency. Animation speed is user-controlled and cannot be read as inference speed.

## Missing evidence

Fresh evaluation metrics (task accuracy, tool correctness, coherence) were not included in the LangSmith trace ZIP. They are excluded from V2.3. If new evaluation files are supplied, add them after verifying they correspond to this same run.
