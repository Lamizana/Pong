"""Écran de fin de partie : annonce le vainqueur et propose de rejouer."""

import pygame

from .. import settings
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
        elif event.key in (pygame.K_q, pygame.K_m):
            self.app.switch_scene("menu")

    def draw(self, surface):
        surface.fill(settings.BLACK)
        center_x = settings.WINDOW_WIDTH // 2
        if self.winner == "left":
            title = "Victoire du joueur 1 !"
        elif self.mode == "1p":
            title = "Victoire de l'IA !"
        else:
            title = "Victoire du joueur 2 !"
        self.app.draw_text(surface, title, self.app.font_large, settings.GREEN,
                           center=(center_x, 220))
        self.app.draw_text(surface, "Entrée : rejouer", self.app.font_small,
                           settings.GRAY, center=(center_x, 320))
        self.app.draw_text(surface, "M ou Q : menu", self.app.font_small,
                           settings.GRAY, center=(center_x, 350))
