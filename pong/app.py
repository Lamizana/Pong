"""Application : initialisation, boucle principale et gestion des scènes."""

import pygame

from . import settings
from .scenes.game import GameScene
from .scenes.menu import MenuScene
from .sound import SoundManager


class App:
    """Possède la fenêtre, l'horloge, le son et la scène courante."""

    def __init__(self, sound_enabled=True):
        pygame.init()
        try:
            self.screen = pygame.display.set_mode(
                (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
            )
        except pygame.error as exc:  # dépend du matériel : message clair plutôt qu'un crash
            raise SystemExit(f"Impossible d'ouvrir la fenêtre de jeu : {exc}")
        pygame.display.set_caption(settings.CAPTION)

        self.clock = pygame.time.Clock()
        self.sound = SoundManager(enabled=sound_enabled)
        self.running = True

        self.font_small = pygame.font.SysFont(None, 28)
        self.font_medium = pygame.font.SysFont(None, 44)
        self.font_large = pygame.font.SysFont(None, 72)

        self._scenes = {"menu": MenuScene, "game": GameScene}
        self.scene = None
        self.switch_scene("menu")

    def switch_scene(self, name, **kwargs):
        """Construit une nouvelle scène et l'active."""
        self.scene = self._scenes[name](self, **kwargs)

    def set_scene(self, scene):
        """Active une scène déjà construite (ex. reprise après pause)."""
        self.scene = scene

    def quit(self):
        self.running = False

    def run(self):
        """Boucle principale, jusqu'à la fermeture de la fenêtre."""
        while self.running:
            # dt plafonné : évite un saut énorme après une pause système.
            dt = min(self.clock.tick(settings.FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    break
                self.scene.handle_event(event)
            else:
                self.scene.update(dt)
                self.scene.draw(self.screen)
                pygame.display.flip()
        pygame.quit()

    def draw_text(self, surface, text, font, color, center=None, topleft=None):
        """Petit utilitaire de rendu de texte, renvoie le rectangle occupé."""
        image = font.render(text, True, color)
        rect = image.get_rect()
        if center is not None:
            rect.center = center
        if topleft is not None:
            rect.topleft = topleft
        surface.blit(image, rect)
        return rect
