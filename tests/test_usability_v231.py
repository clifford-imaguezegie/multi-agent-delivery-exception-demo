from pathlib import Path
import sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from replay_data import load_data
from agent_flow import build_replay_html


def test_visitor_friendly_pace_is_default_and_manual_remains_available():
    case=next(c for c in load_data()['cases'] if c['id']=='SHP-006')
    text=build_replay_html(case)
    assert '<option value="reading" selected>Comfortable' in text
    assert '<option value="relaxed">Extra reading time' in text
    assert '<option value="overview">Quick overview' in text
    assert '<option value="manual">Manual · one step at a time' in text
    assert 'readingDelay(steps[index])' in text
    assert 'Next step in ' in text
    assert 'performance.now()+delay' in text
    assert "document.addEventListener('visibilitychange'" in text


def test_version_footer_on_every_page():
    app=(ROOT/'app.py').read_text()
    css=(ROOT/'style.css').read_text()
    assert 'APP_VERSION = "2.3.1"' in app
    assert 'TRACE_BATCH_LABEL = "17 October 2026"' in app
    assert 'APP VERSION' in app and 'release-tag' in app
    assert "else:results()" in app and "st.markdown(f'''<div class=\"footer-note\"" in app
    assert '.release-tag' in css


def test_capture_unchanged_by_reading_updates():
    old=Path('/mnt/data/delivery_exception_replay_v2_3/data/recorded_cases.json')
    new=ROOT/'data'/'recorded_cases.json'
    if old.exists():
        assert sha256(old.read_bytes()).hexdigest()==sha256(new.read_bytes()).hexdigest()
    cases=load_data()['cases']
    assert len(cases)==10
    assert [c['id'] for c in cases]==[f'SHP-{i:03d}' for i in range(1,11)]
