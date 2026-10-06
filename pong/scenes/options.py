"""Écran Options : réglage de la difficulté et des points pour gagner."""

import pygame

from .. import config, settings, ui
from .base import Scene

_ROW_LEVEL = 0
_ROW_POINTS = 1


class OptionsScene(Scene):
    """Sous-menu de réglages, accessible depuis le menu principal."""

    def __init__(self, app):
        super().__init__(app)
        self.index = 0
        self.frame = ui.fit_menu_frame(app.assets.menu_frame)

    # --- Événements ---

    def handle_event(self, event):
        new_index = ui.navigation_index(event, self.index, len(self._rows()))
        if new_index is not None:
            self.index = new_index
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_HOME:
            self.app.switch_scene("start")
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
        config_now = self.app.config
        if self.index == _ROW_LEVEL:
            keys = list(settings.AI_LEVELS)
            config_now["level"] = keys[(keys.index(config_now["level"]) + delta) % len(keys)]
        elif self.index == _ROW_POINTS:
            choices = settings.POINT_CHOICES
            current = choices.index(config_now["points_to_win"])
            config_now["points_to_win"] = choices[(current + delta) % len(choices)]
        else:
            return
        config.save(config_now)

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
        frame_rect = ui.panel_rect(self.frame)
        surface.blit(self.frame, frame_rect)

        labels = [f"{label} : {value}" if value else label
                  for label, value in self._rows()]
        ui.draw_choices(surface, self.app, frame_rect, labels, self.index)
        ui.draw_hint(surface, self.app,
                     "Flèches ←/→ : changer     Entrée : retour     Échap : accueil")
