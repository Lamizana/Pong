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


def test_readme_shows_every_screenshot():
    """Chaque capture du dépôt est montrée : pas de fichier orphelin."""
    readme = _read("README.md")

    for name in ("start.png", "menu.png", "game.png", "gameover.png"):
        assert name in readme, f"{name} n'est pas montré dans le README"
        assert (ROOT / "docs" / "screenshots" / name).exists()


def test_tutorial_uses_current_values():
    for path in (ROOT / "docs" / "tutoriel").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert "PADDLE_HEIGHT = 100" not in text, path.name
        assert "POINTS_TO_WIN = 7" not in text, path.name
        assert "1 joueur — Difficile" not in text, path.name


def test_physics_chapter_mentions_circle_collision():
    assert "circle_rect_contact" in _read("docs/tutoriel/05-la-balle-et-la-physique.md")


def test_score_chapter_uses_current_gameover_signature():
    chapter = _read("docs/tutoriel/07-score-et-victoire.md")

    assert "self.level)" not in chapter
    assert "GameOverScene(self.app, winner, self.mode)" in chapter


def test_tutorial_does_not_use_removed_constants():
    dead = ("settings.BLACK", "settings.WHITE", "settings.GRAY",
            "settings.ACCENT", "settings.RED", "settings.GREEN",
            "NEON_PURPLE", "SKY_TOP")
    for path in (ROOT / "docs" / "tutoriel").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for name in dead:
            assert name not in text, f"{path.name} utilise {name}"


def test_theme_chapter_documents_assets_pipeline():
    chapter = _read("docs/tutoriel/12-theme-et-assets.md")

    assert "SynthwaveBackground" not in chapter
    assert "prepare_assets" in chapter
