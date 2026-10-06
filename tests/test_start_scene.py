"""Tests de l'écran-titre : animation en boucle et passage au menu."""

import pygame

from pong import settings
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

    for _ in range(8):
        app.scene.update(0.05)
        app.scene.draw(app.screen)


def test_any_key_goes_to_menu():
    for code in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_a, pygame.K_LEFT):
        app = App(sound_enabled=False)

        app.scene.handle_event(_key(code))

        assert isinstance(app.scene, MenuScene), code


def test_animation_loops_back_to_start():
    app = App(sound_enabled=False)
    scene = app.scene
    count = len(scene.frames)

    # Un tour complet + une frame : on doit revenir au début de l'animation.
    scene.update((count + 1) / settings.START_VIDEO_FPS)

    assert scene._index() == 1


def test_video_fps_matches_assets_pipeline():
    """Le fps de lecture doit rester aligné sur celui de l'extraction."""
    from scripts import prepare_assets

    assert settings.START_VIDEO_FPS == prepare_assets.START_VIDEO_FPS
