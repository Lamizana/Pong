"""Application : initialisation, boucle principale et gestion des scènes."""

import pygame

from . import config, settings
from .resources import AssetStore, asset_path
from .scenes.game import GameScene
from .scenes.menu import MenuScene
from .scenes.options import OptionsScene
from .scenes.start import StartScene
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

        # Images partagées par toutes les scènes (thème cyberpunk).
        self.assets = AssetStore()

        # Réglages modifiables depuis les options, conservés entre deux sessions.
        self.config = config.load()

        # Police du thème (Orbitron), embarquée dans les assets.
        font_path = str(asset_path(settings.ASSET_FONT))
        self.font_small = pygame.font.Font(font_path, settings.FONT_SMALL_SIZE)
        self.font_medium = pygame.font.Font(font_path, settings.FONT_MEDIUM_SIZE)
        self.font_large = pygame.font.Font(font_path, settings.FONT_LARGE_SIZE)

        self._scenes = {"start": StartScene, "menu": MenuScene, "game": GameScene,
                        "options": OptionsScene}
        self.scene = None
        self.switch_scene("start")

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
        try:
            while self.running:
                # dt plafonné : évite un saut énorme après une pause système.
                dt = min(self.clock.tick(settings.FPS) / 1000.0, 0.05)
                # On fige la scène du début d'image : un changement de scène en
                # cours d'événement ne doit pas rediriger le reste de l'image.
                scene = self.scene
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                        break
                    scene.handle_event(event)
                else:
                    scene.update(dt)
                    scene.draw(self.screen)
                    pygame.display.flip()
        finally:
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
