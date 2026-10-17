"""Evidence-faithful decision package summaries for recorded replay cases.

Resolution is a taxonomy label, while the operational instruction, communication
and supervisor routing are separately recorded outcomes. No real-world action
is performed by this application.
"""
from __future__ import annotations


def label(code: str | None) -> str:
    if not code or code == "N/A":
        return "No action required"
    return str(code).replace("_", " ").strip().capitalize()


def decision_package(case: dict) -> dict:
    f = case["final_action"]
    res = case["resolution_agent"]
    comm = case["communication_agent"]
    routine = f["is_exception"] != "YES"
    op = res.get("operational_action")
    contact_requested = bool(op and "CONTACT_CUSTOMER" in op)
    message_drafted = bool(comm.get("communication_message"))
    escalated = bool(f["escalated"])
    triggers = list(case["escalation_signals"].get("triggers", []))
    if routine:
        customer = "Not required — routine event filtered"
        supervisor = "Not required"
        operational = "Routine event: no shipment intervention"
    else:
        customer = (
            "Customer contact requested; draft prepared (not sent)" if contact_requested and message_drafted else
            "Customer contact requested; no draft recorded" if contact_requested else
            "Customer message drafted (not sent)" if message_drafted else
            "No customer message captured"
        )
        supervisor = ("Supervisor review / approval required" if escalated else "No final supervisor escalation")
        operational = label(op) if op else "Not recorded"
    return {
        "is_routine": routine,
        "primary": label(f.get("resolution")) if not routine else "Routine event filtered",
        "operational": operational,
        "operational_code": op,
        "customer": customer,
        "supervisor": supervisor,
        "escalation_triggers": triggers,
        "escalated": escalated,
        "validation": f"{f['revision_count']} resolution revision(s); independent checks recorded" if not routine else "Deterministic fast path (no AI-agent review)",
        "draft_available": message_drafted,
        "customer_contact_requested": contact_requested,
        "recorded_latency_seconds": case["metrics"]["latency_seconds"],
    }
