"""Vérifie que `conftest.py` prépare pygame avant chaque test (fixture autouse)."""

import pygame


def test_display_is_ready_without_manual_setup():
    assert pygame.display.get_surface() is not None


def test_font_module_is_usable_without_manual_setup():
    assert pygame.font.get_init()
