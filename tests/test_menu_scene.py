"""Tests du menu principal : navigation et retour à l'écran d'accueil."""

import pygame

from pong.app import App
from pong.scenes.start import StartScene

def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)

def test_escape_returns_to_home_screen():
    app = App(sound_enabled=False)
    app.switch_scene("menu")

    app.scene.handle_event(_key(pygame.K_ESCAPE))

    assert isinstance(app.scene, StartScene)

def test_arrow_keys_move_selection():
    app = App(sound_enabled=False)
    app.switch_scene("menu")

    app.scene.handle_event(_key(pygame.K_DOWN))

    assert app.scene.index == 1
