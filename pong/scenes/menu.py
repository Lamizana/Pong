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
        surface.blit(self.app.assets.menu_background, (0, 0))
        center_x = settings.WINDOW_WIDTH // 2

        # Cadre décoratif, centré sur l'écran.
        frame = self.app.assets.menu_frame
        frame_rect = frame.get_rect(center=(center_x, settings.WINDOW_HEIGHT // 2))
        surface.blit(frame, frame_rect)

        # Titre, dans la zone haute du cadre.
        synthwave.glow_text(surface, self.app.font_large, settings.CAPTION.upper(),
                            settings.NEON_CYAN,
                            center=(center_x, frame_rect.top + 56), spread=4)

        # Options, centrées verticalement dans le cadre.
        spacing = 60
        first_y = frame_rect.centery - (len(self.options) - 1) * spacing // 2
        for i, (label, _, _) in enumerate(self.options):
            selected = i == self.index
            color = settings.NEON_PINK if selected else settings.TEXT_DIM
            prefix = "> " if selected else "  "
            center = (center_x, first_y + i * spacing)
            if selected:
                synthwave.glow_text(surface, self.app.font_medium, prefix + label,
                                    color, center=center, spread=2)
            else:
                self.app.draw_text(surface, prefix + label, self.app.font_medium, color,
                                   center=center)

        self.app.draw_text(surface, "Flèches ou Z/S : naviguer     Entrée : valider",
                           self.app.font_small, settings.TEXT_DIM,
                           center=(center_x, settings.WINDOW_HEIGHT - 40))
