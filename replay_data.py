"""Public, allowlisted LangSmith-stage replay dataset; no runtime external calls."""
from __future__ import annotations
import json
from pathlib import Path
DATA_PATH=Path(__file__).resolve().parent/'data'/'recorded_cases.json'

def load_data(path:Path=DATA_PATH)->dict:
    data=json.loads(Path(path).read_text(encoding='utf8'))
    validate_data(data)
    return data

def validate_data(data:dict)->None:
    cases=data.get('cases',[])
    assert data.get('replay_mode') is True
    assert len(cases)==10 and [c['id'] for c in cases]==[f'SHP-{i:03}' for i in range(1,11)]
    assert all(c.get('agent_events') and c.get('final_action') and c['metrics']['latency_seconds']>=0 for c in cases)
    assert data['aggregate']['total_spans']==sum(c['trace_summary']['spans_recorded'] for c in cases)
    assert round(sum(c['metrics']['latency_seconds'] for c in cases)/10,2)==data['aggregate']['mean_latency_seconds']

def evaluation_rows(data:dict)->list[dict]:
    return [{
      'Shipment':c['id'], 'Scenario':c['title'],
      'Recorded stages':len(c['agent_events']),
      'Recorded spans':c['trace_summary']['spans_recorded'],
      'Latency (s)':c['metrics']['latency_seconds'],
      'Resolution':c['final_action']['resolution'],
      'Operational handling':c['resolution_agent'].get('operational_action') or 'N/A',
      'Resolution reviews':' → '.join(e.get('review',{}).get('decision','') for e in c['agent_events'] if e['node']=='critic_resolution') or 'N/A',
      'Communication review':' → '.join(e.get('review',{}).get('decision','') for e in c['agent_events'] if e['node']=='critic_communication') or 'N/A',
      'Revisions':c['final_action']['revision_count'],
      'Human escalation': 'YES' if c['final_action']['escalated'] else 'NO',
    } for c in data['cases']]
