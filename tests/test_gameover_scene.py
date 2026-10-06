"""Tests de l'écran de fin de partie : menu Rejouer / Menu navigable."""

import pygame

from pong.app import App
from pong.scenes.game import GameScene
from pong.scenes.gameover import GameOverScene
from pong.scenes.menu import MenuScene
from pong.scenes.start import StartScene

def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)

def _game_over(app):
    """Place une scène de fin de partie (victoire joueur 1, mode 1 joueur)."""
    app.set_scene(GameOverScene(app, "left", "1p"))
    return app.scene

def test_arrow_keys_move_selection():
    app = App(sound_enabled=False)
    scene = _game_over(app)

    scene.handle_event(_key(pygame.K_DOWN))
    assert scene.index == 1
    scene.handle_event(_key(pygame.K_UP))
    assert scene.index == 0

def test_validate_replay_restarts_in_same_mode():
    app = App(sound_enabled=False)
    scene = _game_over(app)
    assert scene.index == 0  # « Rejouer »

    scene.handle_event(_key(pygame.K_RETURN))

    assert isinstance(app.scene, GameScene)
    assert app.scene.mode == "1p"

def test_validate_menu_returns_to_menu():
    app = App(sound_enabled=False)
    scene = _game_over(app)
    scene.handle_event(_key(pygame.K_DOWN))  # « Menu »

    scene.handle_event(_key(pygame.K_RETURN))

    assert isinstance(app.scene, MenuScene)

def test_menu_key_returns_to_menu():
    app = App(sound_enabled=False)
    scene = _game_over(app)

    scene.handle_event(_key(pygame.K_m))

    assert isinstance(app.scene, MenuScene)

def test_escape_returns_to_home_screen():
    app = App(sound_enabled=False)
    scene = _game_over(app)

    scene.handle_event(_key(pygame.K_ESCAPE))

    assert isinstance(app.scene, StartScene)

def test_gameover_draws_without_error():
    app = App(sound_enabled=False)
    scene = _game_over(app)

    scene.draw(app.screen)

