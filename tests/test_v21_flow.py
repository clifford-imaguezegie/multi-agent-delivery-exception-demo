"""V2.1 consistency, scope and actual trace checks."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from replay_data import load_data
from decision_package import decision_package
from agent_flow import trace_steps, build_replay_html


def test_all_event_sequences_are_exact_and_have_no_invented_node_times():
    for case in load_data()['cases']:
        steps=trace_steps(case)
        assert [s['source'] for s in steps] == case['trajectory']
        assert all(s['timing'] is None for s in steps)
        assert all(s['node'] in {'preprocessor','orchestrator','resolution_agent','resolution_critic','communication_agent','communication_critic','finalizer'} for s in steps)


def test_revisions_and_return_path_are_preserved():
    cases={c['id']:c for c in load_data()['cases']}
    steps=trace_steps(cases['SHP-004'])
    assert sum(s['source']=='critic_resolution: decision=REVISE' for s in steps)==2
    assert sum('REVISE loop' in s['source'] for s in steps)==1
    assert any('Max resolution revision loops' in s['source'] for s in steps)
    assert [s['node'] for s in trace_steps(cases['SHP-001'])] == ['preprocessor','preprocessor','orchestrator','finalizer']
    assert any('ValidationError' in s['source'] for s in trace_steps(cases['SHP-003']))


def test_full_decision_package_preserves_outcome_and_constraints():
    cases={c['id']:c for c in load_data()['cases']}
    p=decision_package(cases['SHP-005'])
    assert p['primary']=='Reroute to locker'
    assert p['operational']=='Hold at depot pending supervisor'
    assert p['escalated']
    assert p['draft_available']
    assert len(p['escalation_triggers'])==2
    p=decision_package(cases['SHP-002'])
    assert p['customer_contact_requested']
    assert 'not sent' in p['customer'].lower()
    assert decision_package(cases['SHP-001'])['is_routine']


def test_playback_labels_no_live_api_and_full_run_only():
    cases=load_data()['cases']
    html=build_replay_html(cases[3])
    assert 'Recorded end-to-end' in html
    assert 'Individual agent durations' in html
    assert 'not captured' in html
    assert 'Play' in html and 'Next' in html and 'Reset' in html
    assert '28.58' in html
    assert 'critic_resolution: decision=REVISE' in html
    assert '<script src=' not in html
    assert 'fetch(' not in html and 'XMLHttpRequest' not in html
    assert 'no models or logistics actions are invoked' in html.lower()


def test_header_and_new_page_are_present():
    app=(ROOT/'app.py').read_text(encoding='utf-8')
    css=(ROOT/'style.css').read_text(encoding='utf-8')
    assert 'Agent flow' in app
    assert 'show_decision_package(case)' in app
    assert 'padding-top: 4.9rem !important' in css
    assert css.count('<style>')==1 and css.count('</style>')==1
