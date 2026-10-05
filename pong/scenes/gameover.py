"""Écran de fin de partie : annonce le vainqueur et propose de rejouer."""

import pygame

from .. import settings, synthwave
from .base import Scene
from .menu import fit_menu_frame


class GameOverScene(Scene):
    """Menu de fin : « Rejouer » (relance dans le même mode) ou « Menu »."""

    def __init__(self, app, winner, mode):
        super().__init__(app)
        self.winner = winner
        self.mode = mode
        self.options = [("Rejouer", "replay"), ("Menu", "menu")]
        self.index = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.P1_UP or event.key in settings.P2_UP:
            self.index = (self.index - 1) % len(self.options)
        elif event.key in settings.P1_DOWN or event.key in settings.P2_DOWN:
            self.index = (self.index + 1) % len(self.options)
        elif event.key in settings.KEY_VALIDATE:
            self._select()
        elif event.key in settings.KEY_MENU:
            self.app.switch_scene("menu")

    def _select(self):
        action = self.options[self.index][1]
        if action == "replay":
            self.app.switch_scene("game", mode=self.mode)
        else:
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

        # Titre du vainqueur, dans la bande haute de la zone sombre du panneau.
        synthwave.glow_text(surface, self.app.font_medium, title, color,
                            center=(center_x, frame_rect.top + int(0.37 * frame_rect.height)),
                            spread=3)

        # Choix, sous le titre ; texte clair sur fond sombre.
        for i, (label, _) in enumerate(self.options):
            selected = i == self.index
            text = ("> " if selected else "  ") + label
            color = settings.NEON_PINK if selected else settings.TEXT_DIM
            center = (center_x, frame_rect.top + int((0.55 + 0.12 * i) * frame_rect.height))
            if selected:
                synthwave.glow_text(surface, self.app.font_small, text, color,
                                    center=center, spread=1)
            else:
                self.app.draw_text(surface, text, self.app.font_small, color,
                                   center=center)

        self.app.draw_text(surface, "Flèches ou Z/S : choisir     Entrée : valider",
                           self.app.font_small, settings.TEXT_DIM,
                           center=(center_x, settings.WINDOW_HEIGHT - 30))
