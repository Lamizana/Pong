"""Tests de l'écran Options : difficulté et points pour gagner."""

import pygame

from pong import settings, ui
from pong.app import App
from pong.scenes.menu import MenuScene
from pong.scenes.options import OptionsScene
from pong.scenes.start import StartScene

def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)

def _select(app, label):
    """Amène la sélection du menu sur `label` puis valide."""
    app.switch_scene("menu")
    for _ in range(len(app.scene.options) + 1):
        if app.scene.options[app.scene.index][0] == label:
            break
        app.scene.handle_event(_key(pygame.K_DOWN))
    app.scene.handle_event(_key(pygame.K_RETURN))

def test_options_scene_is_reachable_from_menu():
    app = App(sound_enabled=False)

    _select(app, "Options")

    assert isinstance(app.scene, OptionsScene)

def test_options_changes_difficulty_in_config():
    app = App(sound_enabled=False)
    app.switch_scene("options")
    scene = app.scene
    scene.index = 0  # ligne « Difficulté »
    before = app.config["level"]

    scene.handle_event(_key(pygame.K_RIGHT))

    assert app.config["level"] != before
    assert app.config["level"] in settings.AI_LEVELS

def test_options_changes_points_in_config():
    app = App(sound_enabled=False)
    app.switch_scene("options")
    scene = app.scene
    scene.index = 1  # ligne « Points pour gagner »
    before = app.config["points_to_win"]

    scene.handle_event(_key(pygame.K_RIGHT))

    assert app.config["points_to_win"] != before
    assert app.config["points_to_win"] in settings.POINT_CHOICES

def test_options_return_row_goes_back_to_menu():
    app = App(sound_enabled=False)
    app.switch_scene("options")
    scene = app.scene
    scene.index = 2  # ligne « Retour »

    scene.handle_event(_key(pygame.K_RETURN))

    assert isinstance(app.scene, MenuScene)

def test_options_escape_returns_to_home_screen():
    app = App(sound_enabled=False)
    app.switch_scene("options")

    app.scene.handle_event(_key(pygame.K_ESCAPE))

    assert isinstance(app.scene, StartScene)

def test_options_pause_key_returns_to_menu():
    app = App(sound_enabled=False)
    app.switch_scene("options")

    app.scene.handle_event(_key(pygame.K_p))

    assert isinstance(app.scene, MenuScene)

def test_options_draws_without_error():
    app = App(sound_enabled=False)
    app.switch_scene("options")

    app.scene.draw(app.screen)

def test_options_does_not_draw_a_title():
    """Le panneau n'affiche plus de titre « OPTIONS » dans sa bande haute."""
    app = App(sound_enabled=False)
    app.switch_scene("options")
    app.scene.draw(app.screen)
    frame_rect = ui.panel_rect(app.scene.frame)

    # Bande occupée par l'ancien titre : police de 72 px centrée à top + 40.
    yellow = tuple(settings.NEON_YELLOW[:3])
    count = sum(
        1
        for y in range(frame_rect.top + 4, frame_rect.top + 76)
        for x in range(frame_rect.centerx - 160, frame_rect.centerx + 160)
        if app.screen.get_at((x, y))[:3] == yellow
    )

    assert count == 0

def test_options_shows_configured_level_label():
    app = App(sound_enabled=False)
    app.config["level"] = "difficile"
    app.switch_scene("options")

    label = app.scene._rows()[0][1]

    assert label == settings.AI_LEVELS["difficile"]["label"]
