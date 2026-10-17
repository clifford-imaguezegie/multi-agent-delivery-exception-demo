from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from replay_data import load_data,evaluation_rows
from review_evidence import critic_timeline,communication_authority
from agent_flow import trace_steps,build_replay_html
from storyline import story_scenes

DATA=load_data()
CASES={c['id']:c for c in DATA['cases']}

def test_all_ten_current_cases_and_spans():
 assert len(CASES)==10 and DATA['aggregate']['total_spans']==428
 assert DATA['aggregate']['mean_latency_seconds']==16.41
 assert DATA['aggregate']['mean_exception_latency_seconds']==20.51
 assert len(evaluation_rows(DATA))==10

def test_new_revision_sequences():
 assert [x['verdict'] for x in critic_timeline(CASES['SHP-003'])['resolution_reviews']]==['REVISE','REVISE']
 assert [x['verdict'] for x in critic_timeline(CASES['SHP-006'])['resolution_reviews']]==['REVISE','ACCEPT']
 assert [x['verdict'] for x in critic_timeline(CASES['SHP-004'])['resolution_reviews']]==['ACCEPT']
 assert critic_timeline(CASES['SHP-007'])['communication_reviews'][0]['verdict']=='ESCALATE'

def test_all_critic_rationales_captured_and_previous_proposals_linked():
 for c in CASES.values():
  audit=critic_timeline(c)
  for e in audit['resolution_reviews']:
   assert len(e['rationale'])>=50 and e['proposal']['resolution']
   assert e['duration_seconds']>0
  for e in audit['communication_reviews']:
   assert len(e['rationale'])>30
   assert e['reviewed_draft'].get('communication_message')

def test_real_agent_stage_timing_and_order():
 for c in CASES.values():
  steps=trace_steps(c)
  assert steps and len(steps)==len(c['agent_events'])
  assert steps[0]['node']=='preprocessor' and steps[-1]['node']=='finalizer'
  assert all(isinstance(s['timing'],float) and s['timing']>=0 for s in steps)
  assert all(b['offset']>=a['offset'] for a,b in zip(steps,steps[1:]))
  assert sum(s['timing'] for s in steps)<=c['metrics']['latency_seconds']+1.0

def test_animation_is_read_only_and_measured():
 h=build_replay_html(CASES['SHP-006'])
 assert 'REVISE' in h and 'ACCEPT' in h
 assert 'stage-time' in h and 'duration_seconds' not in h or 'stage-time' in h
 assert 'Play' in h and 'Reset' in h
 assert '<script src=' not in h and 'fetch(' not in h and 'XMLHttpRequest' not in h
 assert '<script' in h

def test_decision_authority_still_explicit():
 assert communication_authority(CASES['SHP-004'])['approval_observed'] is False
 assert communication_authority(CASES['SHP-004'])['is_escalated']
 assert not communication_authority(CASES['SHP-001'])['draft_available']

def test_story_and_video_match_latest_capture():
 for c in CASES.values():
  scenes=story_scenes(c)
  assert len(scenes)>=4
  assert any('FINAL' in s['label'] for s in scenes)
 assert (ROOT/'assets'/'shp006_story.mp4').stat().st_size>50000
 assert not (ROOT/'assets'/'shp004_story.mp4').exists()

def test_public_data_allowlisted_and_no_known_identifiers():
 text=(ROOT/'data'/'recorded_cases.json').read_text()
 for banned in ['Michael','Maria','Emily','John Smith','CUST-','@','playbook_context','customer_profile_full','api_key','dotted_order','root_run_id','trace_id']:
  assert banned.lower() not in text.lower(),banned
 assert not re.search(r'\b\d{5}\b',text)
 assert 'recipient_address' not in text
 assert all(not set(c).intersection({'raw_rows','inputs','outputs','prompt'}) for c in CASES.values())
 assert all(e['node'] in {'preprocessor','orchestrator','resolution_agent','critic_resolution','communication_agent','critic_communication','finalize'} for c in CASES.values() for e in c['agent_events'])

def test_current_evaluation_not_mislabeled():
 app=(ROOT/'app.py').read_text()
 assert '16.41' in app or 'mean_latency_seconds' in app
 assert 'not carried over' in app.lower()
 assert 'Task completion' not in app
 assert '5 / 5' not in app

def test_web_app_no_llm_or_extra_server_dependencies():
 req=(ROOT/'requirements.txt').read_text().lower()
 assert all(bad not in req for bad in ('langchain','fastapi','langgraph','openai','openrouter'))
 assert 'streamlit' in req
 assert len(list(ROOT.rglob('*.zip')))==0
