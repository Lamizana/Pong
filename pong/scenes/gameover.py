"""Écran de fin de partie : annonce le vainqueur et propose de rejouer."""

import pygame

from .. import settings, synthwave
from .base import Scene


class GameOverScene(Scene):
    def __init__(self, app, winner, mode, level):
        super().__init__(app)
        self.winner = winner
        self.mode = mode
        self.level = level

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_VALIDATE:
            self.app.switch_scene("game", mode=self.mode, level=self.level)
        elif event.key in settings.KEY_MENU:
            self.app.switch_scene("menu")

    def draw(self, surface):
        surface.blit(self.app.assets.background, (0, 0))
        center_x = settings.WINDOW_WIDTH // 2

        # Panneau translucide derrière le texte.
        panel = pygame.Surface((settings.WINDOW_WIDTH, 260), pygame.SRCALPHA)
        panel.fill((*settings.SKY_TOP, 165))
        surface.blit(panel, (0, 130))

        if self.winner == "left":
            title = "Victoire du joueur 1 !"
            color = settings.NEON_CYAN
        elif self.mode == "1p":
            title = "Victoire de l'IA !"
            color = settings.NEON_PINK
        else:
            title = "Victoire du joueur 2 !"
            color = settings.NEON_PINK
        synthwave.glow_text(surface, self.app.font_large, title, color,
                            center=(center_x, 220), spread=5)
        self.app.draw_text(surface, "Entrée : rejouer", self.app.font_small,
                           settings.TEXT_COLOR, center=(center_x, 320))
        self.app.draw_text(surface, "M ou Q : menu", self.app.font_small,
                           settings.TEXT_DIM, center=(center_x, 350))
