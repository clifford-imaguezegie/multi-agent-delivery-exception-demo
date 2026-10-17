"""Repository structure must remain deployable while the root stays clean."""
from pathlib import Path
import hashlib
from src.replay_data import load_data

ROOT = Path(__file__).resolve().parents[1]

def test_entry_point_and_assets():
    assert (ROOT / "app.py").is_file()
    assert (ROOT / "requirements.txt").is_file()
    assert (ROOT / "src" / "__init__.py").is_file()
    assert (ROOT / "assets" / "style.css").is_file()
    assert (ROOT / "assets" / "shp006_story.mp4").is_file()
    assert len(load_data()["cases"]) == 10

def test_readme_releases_at_bottom_and_project_intro_at_top():
    content=(ROOT / "README.md").read_text()
    assert content.startswith("# Exception / Control")
    assert content.index("## The operational challenge") < content.index("## Version and release history")
    assert "v2.4.0" in content[content.index("## Version and release history"):]

def test_no_private_or_root_helper_files():
    top_files={p.name for p in ROOT.iterdir() if p.is_file()}
    assert top_files == {"app.py","requirements.txt","README.md",".gitignore"}
    assert not list(ROOT.rglob("*.zip"))
    assert not list(ROOT.rglob("*.ipynb"))
