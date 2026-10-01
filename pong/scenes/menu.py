"""Menu principal : choix du mode de jeu."""

import pygame

from .. import settings
from .base import Scene


class MenuScene(Scene):
    """Écran d'accueil listant les modes de jeu."""

    def __init__(self, app):
        super().__init__(app)
        # Les libellés de difficulté viennent de settings.AI_LEVELS (source unique).
        self.options = [
            (config["label"], "game", {"mode": "1p", "level": key})
            for key, config in settings.AI_LEVELS.items()
        ]
        self.options += [
            ("2 joueurs", "game", {"mode": "2p"}),
            ("Quitter", None, None),
        ]
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

    def _select(self):
        _, scene_name, kwargs = self.options[self.index]
        if scene_name is None:
            self.app.quit()
        else:
            self.app.switch_scene(scene_name, **kwargs)

    def draw(self, surface):
        surface.fill(settings.BLACK)
        center_x = settings.WINDOW_WIDTH // 2
        self.app.draw_text(surface, settings.CAPTION.upper(), self.app.font_large,
                           settings.ACCENT, center=(center_x, 120))
        for i, (label, _, _) in enumerate(self.options):
            selected = i == self.index
            color = settings.WHITE if selected else settings.GRAY
            prefix = "> " if selected else "  "
            self.app.draw_text(surface, prefix + label, self.app.font_medium, color,
                               center=(center_x, 240 + i * 60))
        self.app.draw_text(surface, "Flèches ou Z/S : naviguer     Entrée : valider",
                           self.app.font_small, settings.DARK_GRAY,
                           center=(center_x, settings.WINDOW_HEIGHT - 40))
