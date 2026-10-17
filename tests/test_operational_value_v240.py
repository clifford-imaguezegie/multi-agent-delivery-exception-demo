"""V2.4.0 is a presentation-only update; verify benefits and measurement boundaries."""
from pathlib import Path
import hashlib
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def test_value_proposition_has_five_distinct_cards():
    app=(ROOT/'app.py').read_text(encoding='utf-8')
    assert 'operational_value()' in app
    for s in (
        'Faster decision preparation',
        'More consistent recommendations',
        'Less fragmented coordination',
        'Decision-ready human handovers',
        'Customer response preparation',
    ):
        assert s in app
    assert 'heading("03 / OPERATIONAL VALUE"' in app
    assert 'heading("04 / THE EVIDENCE"' in app
    assert app.count('("01", "DECISION SPEED"')==1


def test_no_unverified_operational_savings_claim():
    app=(ROOT/'app.py').read_text(encoding='utf-8')
    assert 'These are proof-of-concept measurements, not measured reductions in manual effort or cost' in app
    assert 'future operational pilot' in app
    assert 'mean_exception_seconds:.2f' in app
    assert '10/10' in app
    assert 'not automatic messages' in app or 'not automatic messages' in app.lower().replace('—',' ')


def test_value_cards_mobile_and_source_safe():
    css=(ROOT/'assets'/'style.css').read_text(encoding='utf-8')
    assert '.value-grid' in css and '.value-card' in css
    assert '@media(max-width:650px)' in css
    assert css.count('<style>')==css.count('</style>')==1
    assert '.value-proof-disclaimer' in css


def test_navigation_and_architecture_preserved():
    app=(ROOT/'app.py').read_text(encoding='utf-8')
    assert 'pages=["The challenge","Architecture","Case stories","Agent flow","Evidence room","Results"]' in app
    assert 'APP_VERSION = "2.4.0"' in app
    assert 'Seven workflow steps. Two models. One accountable system.' in app


def test_app_still_read_only():
    req=(ROOT/'requirements.txt').read_text().lower()
    assert 'streamlit' in req
    assert all(s not in req for s in ('fastapi','requests','openrouter','langchain'))
