"""Recorded story and responsible-performance-claim tests."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from replay_data import load_data
from storyline import story_scenes
ROOT=Path(__file__).resolve().parents[1]

def test_one_story_for_each_case_and_evidence_remains_captured():
    d=load_data()
    for c in d['cases']:
        scenes=story_scenes(c)
        assert len(scenes)>=4
        assert scenes[0]['label'].startswith('01')
        assert any('final' in s['label'].lower() for s in scenes)
        assert any(c['id'] in s['summary'] for s in scenes)
        valid_lines=set(c['trajectory'])
        for sc in scenes:
            assert len(sc['summary'])>20
            for line in sc['evidence']:
                if ':' in line and line.split(':')[0] in ('preprocessor','orchestrator','resolution_agent','critic_resolution','communication_agent','critic_communication','finalize'):
                    assert line in valid_lines

def test_latency_basis_and_extra_claims():
    cases=load_data()['cases']
    actual=[c['metrics']['latency_seconds'] for c in cases if c['final_action']['is_exception']=='YES']
    assert len(actual)==8
    assert round(sum(actual)/len(actual),2)==17.32
    assert min(actual)==8.41 and max(actual)==32.65
    assert round(sum(c['metrics']['latency_seconds'] for c in cases)/len(cases),2)==13.86

def test_generated_video_exists_and_app_contains_clear_disclaimer():
    assert (ROOT/'assets'/'shp004_story.mp4').stat().st_size>50000
    app=(ROOT/'app.py').read_text()
    assert 'not live' in app.lower() or 'not a live' in app.lower()
    assert 'no ai inference' in app.lower()
    assert 'not representative production performance' in app.lower()
    assert 'story_scenes' in app
    assert 'st.video' in app

def test_no_external_scripts_or_dependency_on_inference():
    css=(ROOT/'style.css').read_text()
    assert 'http' not in css
    assert not any(s in (ROOT/'requirements.txt').read_text().lower() for s in ('langgraph', 'openai', 'langchain', 'openrouter', 'fastapi'))
