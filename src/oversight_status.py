"""Differentiate recorded escalation requests, agent review and human authorisation.

Authoritative observed outcome = LangSmith finalizer state. Ground-truth labels
are a *separate benchmark expectation* and are never allowed to override evidence.
"""
from __future__ import annotations


def oversight_status(case: dict) -> dict:
    action=case['final_action']
    triggers=case.get('escalation_signals', {}).get('triggers', [])
    events=case.get('agent_events', [])
    routine=action.get('is_exception') != 'YES'
    escalated=bool(action.get('escalated'))
    res_review=[e.get('review',{}).get('decision') for e in events if e.get('node')=='critic_resolution']
    comm_review=[e.get('review',{}).get('decision') for e in events if e.get('node')=='critic_communication']
    auto=[s for s in triggers if s.startswith('AUTOMATIC:')]
    discretionary=[s for s in triggers if s.startswith('DISCRETIONARY:')]
    notes=[]
    if routine:
        headline='Routine event — no agent review or human escalation'
        explanation='Deterministic preprocessing filtered the event. No Resolution Agent, Critic, or supervisor was required.'
    elif not escalated:
        headline='No supervisor escalation requested'
        explanation='The recorded workflow reached a final recommendation without flagging the case for human review.'
        if 'REVISE' in res_review or 'REVISE' in comm_review:
            notes.append('An AI Critic requested a revision. Internal agent review is not the same as human supervisor review.')
    else:
        headline='Supervisor escalation requested — not completed in this replay'
        if auto:
            notes.extend(auto)
        if discretionary:
            notes.extend(discretionary)
        if 'ESCALATE' in comm_review:
            notes.append('Communication Critic escalated the customer-draft review.')
        if 'ESCALATE' in res_review:
            notes.append('Resolution Critic escalated the recommendation.')
        if action.get('revision_count',0)>=2 and 'ESCALATE' not in res_review:
            notes.append('Orchestrator flagged escalation after the two-revision limit.')
        if not notes:
            notes.append('Recorded finalizer requested escalation; a specific trigger was not preserved in the public summary.')
        explanation='The finalizer flagged a need for human oversight. The replay does not show that a supervisor received, reviewed, or approved the case.'
    gt=str(case.get('ground_truth',{}).get('escalation','')).upper().strip()
    expectation=None if gt not in ('YES','NO') else gt=='YES'
    benchmark_disagrees=expectation is not None and expectation!=escalated
    return {'routine':routine,'escalated':escalated,'headline':headline,'explanation':explanation,
            'reasons':notes, 'benchmark_expected':expectation,'benchmark_disagrees':benchmark_disagrees,
            'recorded_human_approval':False}
