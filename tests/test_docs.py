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


def test_tutorial_is_removed():
    """Le cours a remplacé le tutoriel : un seul document à maintenir."""
    assert not (ROOT / "docs" / "tutoriel").exists()
    assert "tutoriel" not in _read("README.md").lower()


def test_packaging_chapter_embeds_assets():
    chapter = _read("docs/cours/12-polish-et-deploiement.md")

    assert "--add-data" in chapter


def test_readme_shows_every_screenshot():
    """Chaque capture du dépôt est montrée : pas de fichier orphelin."""
    readme = _read("README.md")

    for name in ("start.png", "menu.png", "game.png", "gameover.png"):
        assert name in readme, f"{name} n'est pas montré dans le README"
        assert (ROOT / "docs" / "screenshots" / name).exists()


def test_course_uses_current_values():
    for path in (ROOT / "docs" / "cours").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert "PADDLE_HEIGHT = 100" not in text, path.name
        assert "POINTS_TO_WIN = 7" not in text, path.name
        assert "1 joueur — Difficile" not in text, path.name


def test_physics_chapter_mentions_circle_collision():
    assert "circle_rect_contact" in _read("docs/cours/05-les-collisions.md")


def test_score_chapter_uses_current_gameover_signature():
    chapter = _read("docs/cours/10-la-fin-de-partie.md")

    assert "self.level)" not in chapter
    assert "GameOverScene(self.app, winner, self.mode)" in chapter


def test_course_does_not_use_removed_constants():
    dead = ("settings.BLACK", "settings.WHITE", "settings.GRAY",
            "settings.ACCENT", "settings.RED", "settings.GREEN",
            "NEON_PURPLE", "SKY_TOP")
    for path in (ROOT / "docs" / "cours").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for name in dead:
            assert name not in text, f"{path.name} utilise {name}"


def test_theme_chapter_documents_assets_pipeline():
    chapter = _read("docs/cours/11-le-theme-par-images.md")

    assert "SynthwaveBackground" not in chapter
    assert "prepare_assets" in chapter


def test_menu_chapter_shows_current_invites():
    """Le corrigé du menu cite l'invite réelle, Échap renvoyant à l'accueil."""
    chapter = _read("docs/cours/08-le-menu-et-les-options.md")

    assert "↑/↓ ou Z/S : naviguer" in chapter
    assert "Échap : accueil" in chapter
    assert "Entrée/Échap : retour" not in chapter


def test_options_chapter_drops_removed_title():
    """Le titre OPTIONS a été supprimé du panneau : le corrigé ne le dessine plus."""
    chapter = _read("docs/cours/08-le-menu-et-les-options.md")

    assert 'draw_text(surface, "OPTIONS"' not in chapter
    assert "KEY_HOME" in chapter


def test_gameover_chapter_shows_current_invites():
    """Le corrigé de la fin de partie cite l'invite réelle et la branche KEY_HOME."""
    chapter = _read("docs/cours/10-la-fin-de-partie.md")

    assert "↑/↓ ou Z/S : choisir" in chapter
    assert "Échap : accueil" in chapter
    assert "KEY_HOME" in chapter


def test_theme_chapter_drops_removed_title_image():
    """title.png n'existe plus (l'écran-titre a pris sa place) : pas de titre fantôme."""
    chapter = _read("docs/cours/11-le-theme-par-images.md")

    assert "title.png" not in chapter


def test_ball_chapter_uses_real_test_and_helper_names():
    """ch.04 : les extraits citent les vrais tests et la vraie méthode de scène."""
    chapter = _read("docs/cours/04-la-balle.md")

    assert "test_bounce_off_top_wall" in chapter
    assert "_control(" not in chapter
    assert "_move_players(keys, dt)" in chapter


def test_collision_chapter_matches_real_tests():
    """ch.05 : la fixture et le test d'angle corrigé correspondent au dépôt."""
    chapter = _read("docs/cours/05-les-collisions.md")

    assert "RECT = pygame.Rect(100, 100, 20, 60)" not in chapter
    assert "vers la gauche, donc vers la raquette droite" not in chapter
    assert "test_contact_on_side_face" in chapter


def test_ai_chapter_uses_real_test_names():
    """ch.06 : le test de niveau inconnu porte son vrai nom."""
    chapter = _read("docs/cours/06-lia.md")

    assert "test_unknown_level_raises_value_error" in chapter
    assert "test_unknown_level_is_rejected" not in chapter


def test_score_chapter_threshold_matches_the_condition():
    """ch.07 : la victoire tombe au n-ième point (>=), pas au n+1."""
    chapter = _read("docs/cours/07-le-score.md")

    assert "`Score(points_to_win=3)` : le troisième point déclare un vainqueur" in chapter
    assert "test_new_score_starts_at_zero" in chapter


def test_menu_chapter_matches_draw_choices_and_pause():
    """ch.08 : draw_choices reçoit le cadre, et le retour au menu se fait depuis la pause."""
    chapter = _read("docs/cours/08-le-menu-et-les-options.md")

    assert "ui.draw_choices(surface, self.app, frame_rect," in chapter
    assert "depuis la pause, le retour au menu (`Q`/`M`)" in chapter


def test_options_chapter_uses_real_test_names():
    """ch.08 : les tests d'options cités sont ceux du dépôt."""
    chapter = _read("docs/cours/08-le-menu-et-les-options.md")

    assert "test_options_changes_difficulty_in_config" in chapter
    assert "test_options_changes_points_in_config" in chapter
    assert "test_options_return_row_goes_back_to_menu" in chapter


def test_sound_chapter_call_sites_and_real_tests():
    """ch.09 : le son de raquette est joué via _after_paddle_hit ; vrais tests cités."""
    chapter = _read("docs/cours/09-sons-et-pause.md")

    assert "_after_paddle_hit" in chapter
    assert "test_tone_length_matches_duration" in chapter


def test_gameover_chapter_uses_navigation_helper():
    """ch.10 : la fin de partie navigue via ui.navigation_index et teste Échap."""
    chapter = _read("docs/cours/10-la-fin-de-partie.md")

    assert "ui.navigation_index(event, self.index, len(self.options))" in chapter
    assert "test_escape_returns_to_home_screen" in chapter


def test_theme_chapter_uses_real_asset_names():
    """ch.11 : pas d'ASSET_TITLE fantôme, raquettes et écran-titre aux vrais noms."""
    chapter = _read("docs/cours/11-le-theme-par-images.md")

    assert "ASSET_TITLE" not in chapter
    assert "remove_dark_green_background" not in chapter
    assert "self.app.assets.raquette" not in chapter
    assert "ASSET_START" in chapter
    assert "start_screen" in chapter


def test_polish_chapter_packaging_matches_project():
    """ch.12 : embarquement sans espace parasite et paquet avec la vidéo d'accueil."""
    chapter = _read("docs/cours/12-polish-et-deploiement.md")

    assert '"pong/assets$SEP pong/assets"' not in chapter
    assert '"pong/assets$SEPpong/assets"' in chapter
    assert "assets/start_video/*" in chapter
    assert "24 copies" in chapter
    assert "code de sortie" not in chapter
