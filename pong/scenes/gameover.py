"""Écran de fin de partie : annonce le vainqueur et propose de rejouer."""

import pygame

from .. import settings, synthwave
from .base import Scene
from .menu import fit_menu_frame


class GameOverScene(Scene):
    def __init__(self, app, winner, mode):
        super().__init__(app)
        self.winner = winner
        self.mode = mode

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_VALIDATE:
            self.app.switch_scene("game", mode=self.mode)
        elif event.key in settings.KEY_MENU:
            self.app.switch_scene("menu")

    def draw(self, surface):
        surface.blit(self.app.assets.background, (0, 0))
        center_x = settings.WINDOW_WIDTH // 2

        # Panneau (rectangle) centré, comme le menu.
        frame = fit_menu_frame(self.app.assets.menu_frame)
        frame_rect = frame.get_rect(center=(center_x, settings.WINDOW_HEIGHT // 2))
        surface.blit(frame, frame_rect)

        if self.winner == "left":
            title = "Victoire du joueur 1 !"
            color = settings.NEON_CYAN
        elif self.mode == "1p":
            title = "Victoire de l'IA !"
            color = settings.NEON_PINK
        else:
            title = "Victoire du joueur 2 !"
            color = settings.NEON_PINK

        # Textes dans la zone centrale du panneau (fond sombre).
        synthwave.glow_text(surface, self.app.font_medium, title, color,
                            center=(center_x, frame_rect.top + int(0.40 * frame_rect.height)),
                            spread=3)
        self.app.draw_text(surface, "Entrée : rejouer", self.app.font_small,
                           settings.TEXT_COLOR,
                           center=(center_x, frame_rect.top + int(0.62 * frame_rect.height)))
        self.app.draw_text(surface, "M ou Q : menu", self.app.font_small,
                           settings.TEXT_DIM,
                           center=(center_x, frame_rect.top + int(0.74 * frame_rect.height)))
