from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from replay_data import load_data, evaluation_rows  # noqa:E402


def test_ten_recorded_scenarios():
    data = load_data()
    assert [c['id'] for c in data['cases']] == [f'SHP-{i:03}' for i in range(1,11)]
    assert len(evaluation_rows(data))==10


def test_aggregate_and_denominators():
    data=load_data()
    assert data['aggregate']['escalation_accuracy_denominator']==8
    assert data['aggregate']['escalation_routing_denominator']==10
    assert sum(c['metrics']['task_completion'] for c in data['cases'])==10
    assert sum(c['metrics']['tool_call_correct'] for c in data['cases'])==10
    assert round(sum(c['metrics']['latency_seconds'] for c in data['cases'])/10,2)==13.86
    assert {c['id']:c['final_action']['revision_count'] for c in data['cases']}['SHP-004']==2
    assert data['cases'][2]['final_action']['revision_count']==1


def test_recorded_replay_not_live_and_no_direct_identifiers():
    path=ROOT/'data'/'recorded_cases.json'
    text=path.read_text(encoding='utf-8')
    data=json.loads(text)
    assert data['replay_mode'] is True
    assert not any(k in data for k in ('api_key','token','customer_database'))
    for banned in ('CUST-','John Smith','Emily Davis','Oak Avenue','140 Birch Lane','12 Pine Road','@'):
        assert banned not in text
    assert not re.search(r'\b\d{5}\b',text)
    assert not any('Content  :' in str(c['playbook_references']) for c in data['cases'])


def test_two_noise_scenarios_did_not_invoke_agents():
    data=load_data()
    for idx in (0,9):
        c=data['cases'][idx]
        assert c['final_action']['is_exception']=='NO'
        assert c['metrics']['latency_seconds']<1
        assert not c['communication_agent']['communication_message']


def test_every_case_stores_source_evidence():
    for c in load_data()['cases']:
        assert len(c['trajectory'])>=2
        assert c['metrics']['coherence_score']>=0
        assert c['final_action']['revision_count']>=0
        assert c['metrics']['task_completion']
