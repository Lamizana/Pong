"""Écran de fin de partie : annonce le vainqueur et propose de rejouer."""

import pygame

from .. import neon, settings, ui
from .base import Scene

# Le titre occupe la bande haute ; les choix se placent en dessous.
_TITLE_Y = 0.37
_CHOICES_TOP = 0.50
_CHOICES_BOTTOM = 0.72


class GameOverScene(Scene):
    """Menu de fin : « Rejouer » (relance dans le même mode) ou « Menu »."""

    def __init__(self, app, winner, mode):
        super().__init__(app)
        self.winner = winner
        self.mode = mode
        self.options = [("Rejouer", "replay"), ("Menu", "menu")]
        self.index = 0
        # Cadre réduit une seule fois (et non à chaque image).
        self.frame = ui.fit_menu_frame(app.assets.menu_frame)

    def handle_event(self, event):
        new_index = ui.navigation_index(event, self.index, len(self.options))
        if new_index is not None:
            self.index = new_index
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_HOME:
            self.app.switch_scene("start")
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

    def _title(self):
        """Texte et couleur du titre, selon le vainqueur et le mode."""
        if self.winner == "left":
            return "Victoire du joueur 1 !", settings.NEON_CYAN
        if self.mode == "1p":
            return "Victoire de l'IA !", settings.NEON_PINK
        return "Victoire du joueur 2 !", settings.NEON_PINK

    def draw(self, surface):
        surface.blit(self.app.assets.background, (0, 0))
        frame_rect = ui.panel_rect(self.frame)
        surface.blit(self.frame, frame_rect)

        title, color = self._title()
        neon.glow_text(surface, self.app.font_medium, title, color,
                       center=(settings.WINDOW_WIDTH // 2,
                               frame_rect.top + int(_TITLE_Y * frame_rect.height)),
                       spread=3)

        ui.draw_choices(surface, self.app, frame_rect,
                        [label for label, _ in self.options], self.index,
                        zone_top=_CHOICES_TOP, zone_bottom=_CHOICES_BOTTOM)
        ui.draw_hint(surface, self.app,
                     "↑/↓ ou Z/S : choisir     Entrée : valider     Échap : accueil")
