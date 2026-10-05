"""Tests de l'écran Options : difficulté et points pour gagner."""

import pygame

from pong import settings
from pong.app import App
from pong.scenes.menu import MenuScene
from pong.scenes.options import OptionsScene


def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


def _select(app, label):
    """Amène la sélection du menu sur `label` puis valide."""
    for _ in range(len(app.scene.options) + 1):
        if app.scene.options[app.scene.index][0] == label:
            break
        app.scene.handle_event(_key(pygame.K_DOWN))
    app.scene.handle_event(_key(pygame.K_RETURN))


def test_options_scene_is_reachable_from_menu():
    app = App(sound_enabled=False)

    _select(app, "Options")

    assert isinstance(app.scene, OptionsScene)
    pygame.quit()


def test_options_changes_difficulty_in_config():
    app = App(sound_enabled=False)
    app.switch_scene("options")
    scene = app.scene
    scene.index = 0  # ligne « Difficulté »
    before = app.config["level"]

    scene.handle_event(_key(pygame.K_RIGHT))

    assert app.config["level"] != before
    assert app.config["level"] in settings.AI_LEVELS
    pygame.quit()


def test_options_changes_points_in_config():
    app = App(sound_enabled=False)
    app.switch_scene("options")
    scene = app.scene
    scene.index = 1  # ligne « Points pour gagner »
    before = app.config["points_to_win"]

    scene.handle_event(_key(pygame.K_RIGHT))

    assert app.config["points_to_win"] != before
    assert app.config["points_to_win"] in settings.POINT_CHOICES
    pygame.quit()


def test_options_return_row_goes_back_to_menu():
    app = App(sound_enabled=False)
    app.switch_scene("options")
    scene = app.scene
    scene.index = 2  # ligne « Retour »

    scene.handle_event(_key(pygame.K_RETURN))

    assert isinstance(app.scene, MenuScene)
    pygame.quit()


def test_options_draws_without_error():
    app = App(sound_enabled=False)
    app.switch_scene("options")

    app.scene.draw(app.screen)

    pygame.quit()


def test_options_shows_configured_level_label():
    app = App(sound_enabled=False)
    app.config["level"] = "difficile"
    app.switch_scene("options")

    label = app.scene._rows()[0][1]

    assert label == settings.AI_LEVELS["difficile"]["label"]
    pygame.quit()
