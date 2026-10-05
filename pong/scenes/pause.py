"""Écran de pause : fige la partie en cours et affiche un overlay."""

import pygame

from .. import neon, settings, ui
from .base import Scene


class PauseScene(Scene):
    """Overlay affiché par-dessus la partie, sans la mettre à jour."""

    def __init__(self, app, game):
        super().__init__(app)
        self.game = game

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_PAUSE or event.key in settings.KEY_VALIDATE:
            self.app.set_scene(self.game)
        elif event.key in settings.KEY_MENU:
            self.app.switch_scene("menu")

    def draw(self, surface):
        self.game.draw(surface)  # partie figée en arrière-plan

        overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        overlay.set_alpha(190)
        overlay.fill(settings.OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))

        center_x = settings.WINDOW_WIDTH // 2
        font_small = self.app.font_small
        title_y, resume_y, menu_y = ui.stacked_centers(
            settings.WINDOW_HEIGHT // 2,
            [self.app.font_large.get_height(),
             font_small.get_height(),
             font_small.get_height()],
            gap=20)
        neon.glow_text(surface, self.app.font_large, "PAUSE",
                       settings.NEON_CYAN, center=(center_x, title_y), spread=4)
        self.app.draw_text(surface, "P ou Entrée : reprendre", font_small,
                           settings.TEXT_COLOR, center=(center_x, resume_y))
        self.app.draw_text(surface, "Q : retour au menu", font_small,
                           settings.TEXT_DIM, center=(center_x, menu_y))
