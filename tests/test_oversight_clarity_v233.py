from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from replay_data import load_data,evaluation_rows
from oversight_status import oversight_status
from storyline import story_scenes
from decision_package import decision_package

CASES={c['id']:c for c in load_data()['cases']}

def test_case_outcomes_and_oversight_from_finalizer():
    flagged={name for name,c in CASES.items() if oversight_status(c)['escalated']}
    routine={name for name,c in CASES.items() if oversight_status(c)['routine']}
    assert flagged=={'SHP-002','SHP-004','SHP-005','SHP-007','SHP-008','SHP-009'}
    assert routine=={'SHP-001','SHP-010'}
    assert not oversight_status(CASES['SHP-006'])['escalated']
    assert not oversight_status(CASES['SHP-003'])['escalated']

def test_agent_revision_is_not_supervisor_review():
    case=CASES['SHP-006']
    status=oversight_status(case)
    assert case['final_action']['revision_count']==1
    assert not status['escalated']
    assert any('not the same as human' in s.lower() for s in status['reasons'])
    assert 'no supervisor escalation' in story_scenes(case)[-3]['title'].lower()

def test_routine_cases_do_not_get_supervision_chapter():
    for id in ['SHP-001','SHP-010']:
        cases=story_scenes(CASES[id])
        assert not oversight_status(CASES[id])['escalated']
        assert all('supervisor review required' not in c['summary'].lower() for c in cases)

def test_escalation_sources_and_truth_gap_visible():
    c3=oversight_status(CASES['SHP-003'])
    assert not c3['benchmark_disagrees'] and c3['benchmark_expected'] is False
    assert not c3['escalated']
    c4=oversight_status(CASES['SHP-004'])
    assert c4['escalated']
    assert any('two-revision limit' in n.lower() for n in c4['reasons'])
    assert any('vip customer' in n.lower() for n in oversight_status(CASES['SHP-002'])['reasons'])
    assert any('discretionary' in n.lower() for n in oversight_status(CASES['SHP-008'])['reasons'])
    assert any('communication critic' in n.lower() for n in oversight_status(CASES['SHP-007'])['reasons'])
    assert not any(oversight_status(CASES[k])['benchmark_disagrees'] for k in CASES)

def test_decision_packages_are_consistent():
    for c in CASES.values():
        state=oversight_status(c)
        package=decision_package(c)
        assert state['escalated']==package['escalated']
        assert not state['recorded_human_approval']
    assert 'requested' in decision_package(CASES['SHP-002'])['supervisor'].lower()
    assert 'no supervisor escalation' in decision_package(CASES['SHP-006'])['supervisor'].lower()

def test_results_have_both_observed_and_expected_outcomes():
    rows=evaluation_rows(load_data())
    assert all('Supervisor escalation requested' in r and 'Benchmark expected escalation' in r for r in rows)
    c3=next(r for r in rows if r['Shipment']=='SHP-003')
    assert c3['Supervisor escalation requested']=='NO' and c3['Benchmark expected escalation']=='NO'
    assert c3['Task check']=='PASS' and c3['Judge coherence /5']==5
