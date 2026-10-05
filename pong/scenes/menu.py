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
        # Cadre redimensionné une fois pour tenir dans le rectangle bleu néon.
        self.frame = self._fit_frame(app.assets.menu_frame)

    @staticmethod
    def _fit_frame(frame):
        """Réduit le cadre pour qu'il tienne dans le rectangle bleu néon."""
        width = settings.FIELD_WIDTH - 40
        height = max(1, round(frame.get_height() * width / frame.get_width()))
        return pygame.transform.smoothscale(frame, (width, height))

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

        # Cadre centré sur le terrain (rectangle bleu néon du fond).
        frame = self.frame
        frame_rect = frame.get_rect(center=(
            (settings.FIELD_LEFT + settings.FIELD_RIGHT) // 2,
            (settings.FIELD_TOP + settings.FIELD_BOTTOM) // 2))
        surface.blit(frame, frame_rect)

        # Titre, dans la bande haute du cadre.
        synthwave.glow_text(surface, self.app.font_large, settings.CAPTION.upper(),
                            settings.NEON_PURPLE,
                            center=(center_x, frame_rect.top + 40), spread=4)

        # Options, dans la zone centrale (cyan) du cadre ; texte sombre lisible.
        zone_top = frame_rect.top + int(0.24 * frame_rect.height)
        zone_bottom = frame_rect.top + int(0.74 * frame_rect.height)
        spacing = max(1, (zone_bottom - zone_top) // len(self.options))
        first_y = zone_top + spacing // 2
        for i, (label, _, _) in enumerate(self.options):
            selected = i == self.index
            color = (0, 0, 0) if selected else (18, 48, 66)
            prefix = "> " if selected else "  "
            self.app.draw_text(surface, prefix + label, self.app.font_small, color,
                               center=(center_x, first_y + i * spacing))

        self.app.draw_text(surface, "Flèches ou Z/S : naviguer     Entrée : valider",
                           self.app.font_small, settings.TEXT_DIM,
                           center=(center_x, settings.WINDOW_HEIGHT - 30))
