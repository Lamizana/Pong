"""Décor et effets visuels du thème rétro synthwave.

Les calculs de géométrie et la génération du champ d'étoiles sont des fonctions
**pures** (testables sans écran). Le rendu est assuré par `SynthwaveBackground`,
et les halos néon par `glow_circle` / `glow_rect` / `glow_text`.
"""

import math
import random

import pygame

from . import settings


# --------------------------------------------------------------------------- #
# Calculs purs
# --------------------------------------------------------------------------- #

def lerp(a, b, t):
    """Interpolation linéaire entre `a` et `b` pour t dans [0, 1]."""
    return a + (b - a) * t


def lerp_color(color_a, color_b, t):
    """Interpole deux couleurs RVB."""
    return tuple(int(round(lerp(color_a[i], color_b[i], t))) for i in range(3))


def horizontal_grid_ys(horizon_y, height, count):
    """Ordonnées des lignes horizontales de la grille, en perspective.

    L'espacement augmente à mesure qu'on s'éloigne de l'horizon.
    """
    ys = []
    span = height - horizon_y
    for i in range(1, count + 1):
        ys.append(int(round(horizon_y + span * (i / count) ** 2)))
    return ys


def vertical_grid_segments(cx, horizon_y, width, height, spacing):
    """Segments verticaux convergeant vers le point de fuite (cx, horizon_y)."""
    segments = []
    k = 0
    while k * spacing <= width:
        offset = k * spacing
        segments.append(((int(cx), int(horizon_y)), (int(cx + offset), int(height))))
        if offset:
            segments.append(((int(cx), int(horizon_y)), (int(cx - offset), int(height))))
        k += 1
    return segments


def generate_stars(count, width, sky_height, seed=0):
    """Champ d'étoiles déterministe : liste de (x, y, luminosité de base)."""
    rng = random.Random(seed)
    return [
        (rng.uniform(0, width), rng.uniform(0, sky_height), rng.uniform(0.4, 1.0))
        for _ in range(count)
    ]


def sun_pulse(time):
    """Facteur de pulsation douce du soleil, proche de 1."""
    return 1.0 + 0.03 * math.sin(time * 1.5)


# --------------------------------------------------------------------------- #
# Rendu
# --------------------------------------------------------------------------- #

class SynthwaveBackground:
    """Décor de fond : ciel, soleil, grille, étoiles et scanlines."""

    def __init__(self, width=settings.WINDOW_WIDTH, height=settings.WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.horizon_y = settings.HORIZON_Y
        self._sky = self._render_sky()
        self._ground = self._render_ground()
        self._sun = self._render_sun()
        self._scanlines = self._render_scanlines()
        self._stars = generate_stars(settings.STAR_COUNT, width, self.horizon_y, seed=7)

    def draw(self, surface, time):
        """Dessine le décor complet à l'instant `time` (en secondes)."""
        surface.blit(self._sky, (0, 0))

        # Soleil : pulsation légère, centré sur l'horizon (sa moitié basse sera
        # recouverte par le sol).
        pulse = sun_pulse(time)
        size = (int(self._sun.get_width() * pulse), int(self._sun.get_height() * pulse))
        sun = pygame.transform.smoothscale(self._sun, size)
        surface.blit(sun, (self.width // 2 - sun.get_width() // 2,
                           self.horizon_y - sun.get_height() // 2))

        # Sol puis grille (la grille passe devant le soleil).
        surface.blit(self._ground, (0, self.horizon_y))
        self._draw_grid(surface)

        self._draw_stars(surface, time)
        surface.blit(self._scanlines, (0, 0))

    # --- Rendu des couches statiques --- #

    def _render_sky(self):
        surface = pygame.Surface((self.width, self.horizon_y))
        for y in range(self.horizon_y):
            t = y / max(1, self.horizon_y - 1)
            pygame.draw.line(surface, lerp_color(settings.SKY_TOP, settings.SKY_HORIZON, t),
                             (0, y), (self.width, y))
        return surface

    def _render_ground(self):
        height = self.height - self.horizon_y
        surface = pygame.Surface((self.width, height))
        for y in range(height):
            t = y / max(1, height - 1)
            pygame.draw.line(surface, lerp_color(settings.GROUND_FAR, settings.GROUND_NEAR, t),
                             (0, y), (self.width, y))
        return surface

    def _render_sun(self):
        radius = settings.SUN_RADIUS
        diameter = radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        for y in range(diameter):
            dy = y - radius
            half = math.sqrt(max(0.0, radius * radius - dy * dy))
            if half <= 0:
                continue
            color = lerp_color(settings.SUN_TOP, settings.SUN_BOTTOM, y / diameter)
            pygame.draw.line(surface, (*color, 255), (radius - half, y), (radius + half, y))

        # Bandes horizontales découpées, de plus en plus larges vers le bas.
        band_y = radius + int(radius * 0.1)
        gap = 3
        while band_y < radius * 2:
            dy = band_y - radius
            half = math.sqrt(max(0.0, radius * radius - dy * dy))
            if half > 0:
                pygame.draw.line(surface, (*settings.SKY_HORIZON, 255),
                                 (radius - half, band_y), (radius + half, band_y))
            band_y += gap
            gap += 1
        return surface

    def _render_scanlines(self):
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        color = (*settings.SCANLINE_COLOR, settings.SCANLINE_ALPHA)
        for y in range(0, self.height, 3):
            pygame.draw.line(surface, color, (0, y), (self.width, y))
        return surface

    # --- Couches dynamiques --- #

    def _draw_grid(self, surface):
        for y in horizontal_grid_ys(self.horizon_y, self.height, settings.GRID_H_LINES):
            pygame.draw.line(surface, settings.GRID_COLOR, (0, y), (self.width, y))
        for (x1, y1), (x2, y2) in vertical_grid_segments(
                self.width // 2, self.horizon_y, self.width, self.height, settings.GRID_SPACING):
            pygame.draw.line(surface, settings.GRID_COLOR, (x1, y1), (x2, y2))

    def _draw_stars(self, surface, time):
        for i, (x, y, base) in enumerate(self._stars):
            twinkle = 0.5 + 0.5 * math.sin(time * 2.0 + i)
            value = int(255 * base * (0.4 + 0.6 * twinkle))
            pygame.draw.rect(surface, (value, value, min(255, value + 20)),
                             (int(x), int(y), 2, 2))


# --------------------------------------------------------------------------- #
# Halos néon
# --------------------------------------------------------------------------- #

def glow_circle(surface, center, radius, color, spread=10, layers=4, max_alpha=120):
    """Halo circulaire néon autour de `center`."""
    size = int((radius + spread) * 2)
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    middle = size // 2
    for layer in range(layers, 0, -1):
        r = int(radius + spread * (layer / layers))
        alpha = int(max_alpha * (1 - (layer - 1) / layers))
        pygame.draw.circle(glow, (*color[:3], alpha), (middle, middle), r)
    surface.blit(glow, (int(center[0]) - middle, int(center[1]) - middle))


def glow_rect(surface, rect, color, spread=8, layers=4, max_alpha=120, radius=6):
    """Halo rectangulaire néon autour de `rect`."""
    width = rect.width + spread * 2
    height = rect.height + spread * 2
    glow = pygame.Surface((width, height), pygame.SRCALPHA)
    for layer in range(layers, 0, -1):
        margin = int(spread * (layer / layers))
        alpha = int(max_alpha * (1 - (layer - 1) / layers))
        inner = pygame.Rect(margin, margin, width - margin * 2, height - margin * 2)
        pygame.draw.rect(glow, (*color[:3], alpha), inner, border_radius=radius)
    surface.blit(glow, (rect.x - spread, rect.y - spread))


def glow_text(surface, font, text, color, center, spread=3):
    """Texte néon : halo diffus puis texte net par-dessus."""
    dim = tuple(min(255, c // 2 + 50) for c in color[:3])
    base = font.render(text, True, dim)
    rect = base.get_rect(center=center)
    for dx in range(-spread, spread + 1, 2):
        for dy in range(-spread, spread + 1, 2):
            if dx or dy:
                surface.blit(base, (rect.x + dx, rect.y + dy))
    surface.blit(font.render(text, True, color), rect)
    return rect
