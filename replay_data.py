"""Recorded replay data and lightweight integrity checks. No external dependencies."""
from __future__ import annotations
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "recorded_cases.json"


def load_data(path: Path = DATA_PATH) -> dict:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_data(d)
    return d


def validate_data(data: dict) -> None:
    cases = data.get("cases", [])
    ids = [c["id"] for c in cases]
    assert data.get("replay_mode") is True, "This app must remain recorded-replay only"
    assert len(cases) == 10 and len(set(ids)) == 10, "Expected exactly ten unique scenarios"
    assert all(c["final_action"].get("revision_count") is not None for c in cases)
    assert all(c.get("trajectory") for c in cases), "Every case must have a captured trajectory"
    assert data["aggregate"]["cases"] == len(cases)
    assert sum(c["metrics"]["task_completion"] for c in cases) == 10
    assert sum(c["metrics"]["tool_call_correct"] for c in cases) == 10
    assert round(sum(c["metrics"]["latency_seconds"] for c in cases)/10,2)==data["aggregate"]["mean_latency_seconds"]


def evaluation_rows(data: dict) -> list[dict]:
    rows=[]
    for c in data["cases"]:
        m=c["metrics"]
        f=c["final_action"]
        gt=c["ground_truth"]
        rows.append({
            "Shipment": c["id"], "Scenario": c["title"],
            "Task": "PASS" if m["task_completion"] else "FAIL",
            "Tools": "PASS" if m["tool_call_correct"] else "FAIL",
            "Escalation": m["escalation_correct"],
            "Coherence / 5": m["coherence_score"],
            "Revisions": f["revision_count"],
            "Latency (s)": m["latency_seconds"],
            "Decision": f["resolution"], "Expected": gt["resolution"],
            "Escalated": "YES" if f["escalated"] else "NO",
            "Expected escalation": gt["escalation"],
        })
    return rows
