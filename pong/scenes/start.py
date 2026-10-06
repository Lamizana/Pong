"""Écran-titre affiché au lancement : « PRESS START » mène au menu principal."""

import math

import pygame

from .. import neon, settings
from .base import Scene

# Centre du rectangle « PRESS START » dans l'asset 900×600 (relevé sur l'image).
START_BUTTON_CENTER = (450, 368)


class StartScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.time = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in settings.KEY_VALIDATE:
            self.app.switch_scene("menu")

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.blit(self.app.assets.start_screen, (0, 0))

        # Pulsation : l'écart du halo oscille doucement (0 → 4).
        spread = 2 + round(2 * math.sin(self.time * 3.0))
        neon.glow_text(surface, self.app.font_medium, "PRESS START",
                       settings.NEON_PINK, center=START_BUTTON_CENTER, spread=spread)
