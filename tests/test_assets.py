"""Tests du chargeur d'assets (chargement, tailles, transparence)."""

import pytest
import pygame

from pong import settings
from pong.resources import AssetStore, asset_path


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

    sprites = (store.paddle_left, store.paddle_right, store.ball,
               store.menu_frame, store.title)
    for sprite in sprites:
        width, height = sprite.get_size()
        for corner in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)):
            assert sprite.get_at(corner).a == 0, f"coin opaque : {corner}"


def test_ball_sprite_matches_collision_diameter():
    """Le sprite de balle coïncide avec le cercle de collision."""
    pygame.display.set_mode((1, 1))

    assert AssetStore().ball.get_width() == 2 * settings.BALL_RADIUS


def test_sprites_have_no_green_fringe():
    """Le chroma-key ne doit pas laisser de liseré vert sur les bords."""
    pygame.display.set_mode((1, 1))
    store = AssetStore()

    for sprite in (store.paddle_left, store.paddle_right, store.ball, store.title):
        width, height = sprite.get_size()
        offending = []
        for y in range(height):
            for x in range(width):
                pixel = sprite.get_at((x, y))
                if 0 < pixel.a < 255 and pixel.g > max(pixel.r, pixel.b) + 20:
                    offending.append((x, y))
        assert not offending, f"{len(offending)} pixels de bord à dominante verte"


def test_bundled_font_asset_exists():
    from pong.resources import asset_path

    assert asset_path(settings.ASSET_FONT).exists()


def test_missing_asset_raises_error_with_path():
    """Un asset absent doit lever une erreur explicite contenant son chemin."""
    with pytest.raises(FileNotFoundError) as excinfo:
        asset_path("absent.png")

    assert "introuvable" in str(excinfo.value)
    assert "absent.png" in str(excinfo.value)


def test_app_uses_bundled_font():
    from pong.app import App
    from pong.resources import asset_path

    app = App(sound_enabled=False)
    expected = pygame.font.Font(str(asset_path(settings.ASSET_FONT)), 28)

    # Même police et même taille → mêmes métriques que font_small.
    assert app.font_small.size("PONG") == expected.size("PONG")
    pygame.quit()
