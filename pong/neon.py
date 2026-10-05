"""Texte néon : halo diffus puis texte net par-dessus."""

import pygame


def glow_text(surface, font, text, color, center, spread=3):
    """Dessine `text` centré sur `center`, entouré d'un halo diffus.

    `spread` : rayon (en pixels) du halo. 1 donne un halo discret, 3-5 un
    halo marqué. Renvoie le rectangle du texte net.
    """
    dim = tuple(min(255, c // 2 + 50) for c in color[:3])
    base = font.render(text, True, dim)
    rect = base.get_rect(center=center)
    for dx in range(-spread, spread + 1, 2):
        for dy in range(-spread, spread + 1, 2):
            if dx or dy:
                surface.blit(base, (rect.x + dx, rect.y + dy))
    surface.blit(font.render(text, True, color), rect)
    return rect
