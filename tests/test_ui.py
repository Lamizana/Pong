"""Tests des helpers d'interface partagés par les scènes à panneau."""

import pygame

from pong import settings, ui


def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


def test_navigation_index_moves_and_wraps():
    assert ui.navigation_index(_key(pygame.K_DOWN), 0, 3) == 1
    assert ui.navigation_index(_key(pygame.K_UP), 0, 3) == 2
    assert ui.navigation_index(_key(settings.P1_DOWN[0]), 2, 3) == 0


def test_navigation_index_ignores_other_keys():
    assert ui.navigation_index(_key(pygame.K_RETURN), 1, 3) is None
    assert ui.navigation_index(pygame.event.Event(pygame.KEYUP, key=pygame.K_UP), 1, 3) is None


def test_fit_menu_frame_reduces_to_field_width():
    pygame.display.set_mode((1, 1))
    frame = pygame.Surface((880, 405))

    fitted = ui.fit_menu_frame(frame)

    assert fitted.get_width() == settings.FIELD_WIDTH - 40
    assert fitted.get_height() == round(405 * (settings.FIELD_WIDTH - 40) / 880)
