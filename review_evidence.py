"""Version 2.3: chronological Critic evidence from allowlisted LangSmith stage spans."""
from __future__ import annotations


def critic_timeline(case:dict) -> dict:
    events=case.get('agent_events',[])
    reviews=[]; comm=[]; proposals=[]
    for e in events:
        if e['node']=='resolution_agent':
            proposals.append({'trace_index':e['index'], **e.get('proposal',{})})
        elif e['node']=='critic_resolution':
            reviews.append({'sequence':len(reviews)+1,'trace_index':e['index'],
                'verdict':e.get('review',{}).get('decision','Not captured'),
                'proposal':e.get('reviewed_proposal',{}),
                'rationale':e.get('review',{}).get('rationale',''),
                'rationale_status':'LangSmith captured; privacy-redacted',
                'duration_seconds':e['duration_seconds']})
        elif e['node']=='critic_communication':
            comm.append({'sequence':len(comm)+1,'trace_index':e['index'],
                'verdict':e.get('review',{}).get('decision','Not captured'),
                'rationale':e.get('review',{}).get('rationale',''),
                'reviewed_draft':e.get('reviewed_draft',{}),
                'rationale_status':'LangSmith captured; privacy-redacted',
                'duration_seconds':e['duration_seconds']})
    last_state=case.get('resolution_critic',{})
    forced=bool(reviews and case['final_action']['revision_count']>=2 and last_state.get('decision')=='ESCALATE' and reviews[-1]['verdict']!='ESCALATE')
    return {'resolution_reviews':reviews,'communication_reviews':comm,'resolution_proposals':proposals,
            'schema_failures':[], 'orchestrator_override':{
                'present':forced,
                'stored_decision':last_state.get('decision') if forced else None,
                'stored_rationale':last_state.get('rationale') if forced else None},
            'unavailable':{'intermediate_critic_rationales':any(not r.get('rationale') for r in reviews),
                           'intermediate_full_agent_drafts':any('rationale' not in p for p in proposals),
                           'individual_agent_durations':False}}


def review_annotations(case:dict) -> dict[int,str]:
    items={}
    for kind in ('resolution_reviews','communication_reviews'):
        for r in critic_timeline(case)[kind]:
            items[r['trace_index']]=r.get('rationale') or 'A verdict was captured but its rationale was not provided.'
    return items


def communication_authority(case:dict) -> dict:
    msg=case.get('communication_agent',{}).get('communication_message','')
    escalated=bool(case.get('final_action',{}).get('escalated'))
    # No live supervisor authorisation and no customer-send tool is captured.
    return {
        'draft_available':bool(msg), 'is_escalated':escalated, 'approval_observed':False,
        'status':('Unsent draft · supervisor review required' if msg and escalated else 'Unsent draft · no final supervisor escalation' if msg else 'No draft generated'),
        'caution':('Supervisor approval and message delivery are not captured. The draft may describe proposed work but does not evidence an authorised or executed action.' if msg and escalated else 'No customer communication was sent; this is an unsent generated draft.' if msg else 'No customer contact required.'),
        'model_gap':('A policy/customer-choice issue is mentioned in the recorded recommendation, but the resolution taxonomy may not express the full range of choices.' if 'choice' in case.get('resolution_agent',{}).get('rationale','').lower() else None),
        'specific_risk':('The draft may imply a replacement commitment despite pending supervisor review. It remains an unsent artefact.' if escalated and 'replacement' in msg.lower() and any(x in msg.lower() for x in ('arrang','process','send','replace')) else None)
    }
