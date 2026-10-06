"""Tests de l'écran-titre « PRESS START » affiché au lancement."""

import pygame

from pong.app import App
from pong.scenes.menu import MenuScene
from pong.scenes.start import StartScene


def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


def test_start_scene_is_the_opening_screen():
    app = App(sound_enabled=False)

    assert isinstance(app.scene, StartScene)


def test_start_scene_draws_without_error():
    app = App(sound_enabled=False)

    app.scene.update(0.016)
    app.scene.draw(app.screen)


def test_start_validates_to_menu():
    app = App(sound_enabled=False)

    app.scene.handle_event(_key(pygame.K_RETURN))

    assert isinstance(app.scene, MenuScene)


def test_start_also_accepts_space():
    app = App(sound_enabled=False)

    app.scene.handle_event(_key(pygame.K_SPACE))

    assert isinstance(app.scene, MenuScene)


def test_start_ignores_other_keys():
    app = App(sound_enabled=False)

    app.scene.handle_event(_key(pygame.K_LEFT))

    assert isinstance(app.scene, StartScene)
