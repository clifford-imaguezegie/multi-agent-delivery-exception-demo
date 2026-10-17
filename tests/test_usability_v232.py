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
    assert '<option value="overview" selected>Quick overview' in text
    assert '<option value="reading">Comfortable' in text
    assert '<option value="relaxed">Extra reading time' in text
    assert '<option value="manual">Manual · one step at a time' in text
    assert 'readingDelay(steps[index])' in text
    assert 'Next step in ' in text
    assert 'performance.now()+delay' in text
    assert "document.addEventListener('visibilitychange'" in text


def test_version_footer_on_every_page():
    app=(ROOT/'app.py').read_text()
    css=(ROOT/'style.css').read_text()
    assert 'APP_VERSION = "2.3.4"' in app
    assert 'TRACE_BATCH_LABEL = "17 October 2026"' in app
    assert 'APP VERSION' in app and 'release-tag' in app
    assert "else:results()" in app and "st.markdown(f'''<div class=\"footer-note\"" in app
    assert '.release-tag' in css


def test_trace_data_refreshed_without_changing_navigation():
    cases=load_data()['cases']
    assert len(cases)==10
    assert [c['id'] for c in cases]==[f'SHP-{i:03d}' for i in range(1,11)]
    app=(ROOT/'app.py').read_text()
    assert 'pages=["The challenge","Architecture","Case stories","Agent flow","Evidence room","Results"]' in app
    assert cases[2]['final_action']['resolution']=='RESCHEDULE'
    assert cases[2]['final_action']['escalated'] is False


def test_slow_reading_modes_are_actually_slower():
    h=build_replay_html(load_data()['cases'][3])
    assert 'reading: {wpm:115, base:9000, min:30000, max:120000}' in h
    assert 'relaxed: {wpm:85, base:14000, min:60000, max:240000}' in h
    assert 'overview: {wpm:300, base:2000, min:6000, max:25000}' in h


def test_css_has_one_closing_style_tag_at_end():
    css=(ROOT/'style.css').read_text(encoding='utf-8')
    assert css.lstrip().startswith('<style>')
    assert css.strip().endswith('</style>')
    assert css.count('<style>')==css.count('</style>')==1
    assert '.footer-note' in css and css.index('.footer-note') < css.index('</style>')
