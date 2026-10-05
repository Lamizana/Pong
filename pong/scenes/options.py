"""Écran Options : réglage de la difficulté et des points pour gagner."""

import pygame

from .. import settings, synthwave
from .base import Scene
from .menu import fit_menu_frame

_ROWS = 3
_ROW_LEVEL = 0
_ROW_POINTS = 1
_ROW_BACK = 2


class OptionsScene(Scene):
    """Sous-menu de réglages, accessible depuis le menu principal."""

    def __init__(self, app):
        super().__init__(app)
        self.index = 0
        self.frame = fit_menu_frame(app.assets.menu_frame)

    # --- Événements ---

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.P1_UP or event.key in settings.P2_UP:
            self.index = (self.index - 1) % _ROWS
        elif event.key in settings.P1_DOWN or event.key in settings.P2_DOWN:
            self.index = (self.index + 1) % _ROWS
        elif event.key == pygame.K_LEFT:
            self._change(-1)
        elif event.key == pygame.K_RIGHT:
            self._change(1)
        elif (event.key in settings.KEY_VALIDATE
              or event.key in settings.KEY_PAUSE
              or event.key in settings.KEY_MENU):
            self.app.switch_scene("menu")

    def _change(self, delta):
        """Fait défiler la valeur de la ligne sélectionnée (boucle circulaire)."""
        config = self.app.config
        if self.index == _ROW_LEVEL:
            keys = list(settings.AI_LEVELS)
            config["level"] = keys[(keys.index(config["level"]) + delta) % len(keys)]
        elif self.index == _ROW_POINTS:
            choices = settings.POINT_CHOICES
            current = choices.index(config["points_to_win"])
            config["points_to_win"] = choices[(current + delta) % len(choices)]

    # --- Affichage ---

    def _rows(self):
        """Libellé et valeur affichés pour chaque ligne."""
        level = settings.AI_LEVELS[self.app.config["level"]]["label"]
        return [
            ("Difficulté", level),
            ("Points pour gagner", str(self.app.config["points_to_win"])),
            ("Retour", ""),
        ]

    def draw(self, surface):
        surface.blit(self.app.assets.menu_background, (0, 0))
        center_x = settings.WINDOW_WIDTH // 2

        frame_rect = self.frame.get_rect(center=(
            (settings.FIELD_LEFT + settings.FIELD_RIGHT) // 2,
            (settings.FIELD_TOP + settings.FIELD_BOTTOM) // 2))
        surface.blit(self.frame, frame_rect)

        synthwave.glow_text(surface, self.app.font_large, "OPTIONS",
                            settings.NEON_YELLOW,
                            center=(center_x, frame_rect.top + 40), spread=4)

        # Lignes dans la zone centrale du cadre ; texte clair (fond sombre).
        rows = self._rows()
        zone_top = frame_rect.top + int(0.26 * frame_rect.height)
        zone_bottom = frame_rect.top + int(0.74 * frame_rect.height)
        spacing = max(1, (zone_bottom - zone_top) // len(rows))
        first_y = zone_top + spacing // 2
        for i, (label, value) in enumerate(rows):
            selected = i == self.index
            color = settings.NEON_PINK if selected else settings.TEXT_DIM
            prefix = "> " if selected else "  "
            text = f"{prefix}{label}" + (f" : {value}" if value else "")
            center = (center_x, first_y + i * spacing)
            if selected:
                synthwave.glow_text(surface, self.app.font_small, text, color,
                                    center=center, spread=2)
            else:
                self.app.draw_text(surface, text, self.app.font_small, color,
                                   center=center)

        self.app.draw_text(surface,
                           "Flèches ←/→ : changer     Entrée/Échap : retour",
                           self.app.font_small, settings.TEXT_DIM,
                           center=(center_x, settings.WINDOW_HEIGHT - 30))
