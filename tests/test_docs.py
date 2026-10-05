"""Tests anti-dérive entre la documentation et le code réel."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def test_readme_announces_configured_points_to_win():
    readme = _read("README.md")

    assert "Premier à 5 points" in readme
    assert "7 points" not in readme


def test_readme_describes_cyberpunk_theme():
    readme = _read("README.md")

    assert "thème synthwave" not in readme
    assert "thème cyberpunk" in readme


def test_packaging_chapter_embeds_assets():
    chapter = _read("docs/tutoriel/11-packaging-deploiement.md")

    assert "--add-data" in chapter
