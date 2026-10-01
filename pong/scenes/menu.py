"""Menu principal : choix du mode de jeu."""

import pygame

from .. import settings, synthwave
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
        self.app.background.draw(surface, pygame.time.get_ticks() / 1000.0)
        center_x = settings.WINDOW_WIDTH // 2

        # Panneau translucide : améliore la lisibilité des options sur le décor.
        panel = pygame.Surface((settings.WINDOW_WIDTH, 360), pygame.SRCALPHA)
        panel.fill((*settings.SKY_TOP, 165))
        surface.blit(panel, (0, 170))

        synthwave.glow_text(surface, self.app.font_large, settings.CAPTION.upper(),
                            settings.NEON_CYAN, center=(center_x, 120), spread=4)
        for i, (label, _, _) in enumerate(self.options):
            selected = i == self.index
            color = settings.NEON_PINK if selected else settings.TEXT_DIM
            prefix = "> " if selected else "  "
            if selected:
                synthwave.glow_text(surface, self.app.font_medium, prefix + label,
                                    color, center=(center_x, 240 + i * 60), spread=2)
            else:
                self.app.draw_text(surface, prefix + label, self.app.font_medium, color,
                                   center=(center_x, 240 + i * 60))
        self.app.draw_text(surface, "Flèches ou Z/S : naviguer     Entrée : valider",
                           self.app.font_small, settings.TEXT_DIM,
                           center=(center_x, settings.WINDOW_HEIGHT - 40))
