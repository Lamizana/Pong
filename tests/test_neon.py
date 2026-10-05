"""Tests du rendu de texte néon."""

import pygame

from pong.neon import glow_text


def test_glow_text_centers_text_and_draws_pixels():
    pygame.display.set_mode((1, 1))
    pygame.font.init()
    surface = pygame.Surface((200, 60), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    font = pygame.font.Font(None, 24)

    rect = glow_text(surface, font, "PONG", (255, 0, 0), center=(100, 30), spread=1)

    assert rect.center == (100, 30)
    assert any(surface.get_at((x, 30))[:3] != (0, 0, 0) for x in range(200))
