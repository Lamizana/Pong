"""Tests du chargeur d'assets (chargement, tailles, transparence)."""

import pygame

from pong import settings
from pong.resources import AssetStore


def test_asset_store_loads_expected_sizes():
    pygame.display.set_mode((1, 1))
    store = AssetStore()

    assert store.background.get_size() == (900, 600)
    assert store.menu_background.get_size() == (900, 600)
    # Le sprite de raquette épouse la hauteur de la zone de frappe.
    assert store.paddle_left.get_height() == settings.PADDLE_HEIGHT
    assert store.paddle_right.get_height() == settings.PADDLE_HEIGHT
    assert max(store.ball.get_size()) <= 24
    assert store.menu_frame.get_width() <= 900
    assert store.score_screen.get_height() == 72
    assert store.title.get_width() == 240


def test_sprites_have_transparent_corners():
    pygame.display.set_mode((1, 1))
    store = AssetStore()

    for sprite in (store.paddle_left, store.paddle_right, store.ball, store.menu_frame):
        width, height = sprite.get_size()
        assert sprite.get_at((0, 0)).a == 0
        assert sprite.get_at((width - 1, height - 1)).a == 0
