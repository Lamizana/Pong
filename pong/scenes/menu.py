"""Menu principal : lancement d'une partie et accès aux options."""

import pygame

from .. import settings, ui
from .base import Scene


class MenuScene(Scene):
    """Écran d'accueil : partie 1 joueur, 2 joueurs, options, quitter."""

    def __init__(self, app):
        super().__init__(app)
        # La difficulté et les points pour gagner se règlent dans les options.
        self.options = [
            ("1 joueur", "game", {"mode": "1p"}),
            ("2 joueurs", "game", {"mode": "2p"}),
            ("Options", "options", {}),
            ("Quitter", None, None),
        ]
        self.index = 0
        # Cadre réduit une fois pour tenir dans le rectangle bleu néon.
        self.frame = ui.fit_menu_frame(app.assets.menu_frame)

    def handle_event(self, event):
        new_index = ui.navigation_index(event, self.index, len(self.options))
        if new_index is not None:
            self.index = new_index
        elif event.type == pygame.KEYDOWN and event.key in settings.KEY_HOME:
            self.app.switch_scene("start")
        elif event.type == pygame.KEYDOWN and event.key in settings.KEY_VALIDATE:
            self._select()

    def _select(self):
        _, scene_name, kwargs = self.options[self.index]
        if scene_name is None:
            self.app.quit()
        else:
            self.app.switch_scene(scene_name, **kwargs)

    def draw(self, surface):
        surface.blit(self.app.assets.menu_background, (0, 0))
        frame_rect = ui.panel_rect(self.frame)
        surface.blit(self.frame, frame_rect)

        ui.draw_choices(surface, self.app, frame_rect,
                        [label for label, _, _ in self.options], self.index)
        ui.draw_hint(surface, self.app,
                     "↑/↓ ou Z/S : naviguer     Entrée : valider     Échap : accueil")
