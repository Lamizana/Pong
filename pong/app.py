"""Application : initialisation, boucle principale et gestion des scènes."""

import pygame

from . import config, settings, ui
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
            pygame.display.set_mode(
                (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.RESIZABLE
            )
        except pygame.error as exc:  # dépend du matériel : message clair plutôt qu'un crash
            raise SystemExit(f"Impossible d'ouvrir la fenêtre de jeu : {exc}")
        pygame.display.set_caption(settings.CAPTION)

        # Surface interne fixe : le jeu se dessine TOUJOURS en 900×600, quelle
        # que soit la taille de la fenêtre. `present()` met ensuite le rendu à
        # l'échelle (letterbox) dans la fenêtre redimensionnable.
        self.screen = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        self.clock = pygame.time.Clock()
        self.sound = SoundManager(enabled=sound_enabled)
        self.running = True
        self._start_music()

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

    def _start_music(self):
        """Boucle la bande-son du jeu (silencieux si l'audio est indisponible)."""
        try:
            path = asset_path(settings.ASSET_MUSIC)
        except FileNotFoundError:
            return  # musique optionnelle
        self.sound.play_music(path)

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
                    if event.type == pygame.VIDEORESIZE:
                        # On ré-applique la taille annoncée : la surface
                        # d'affichage suit le redimensionnement de la fenêtre.
                        pygame.display.set_mode(event.size, pygame.RESIZABLE)
                        continue
                    scene.handle_event(event)
                else:
                    scene.update(dt)
                    scene.draw(self.screen)
                    self.present()
        finally:
            pygame.quit()

    def present(self):
        """Affiche le canvas dans la fenêtre, centré au même ratio (letterbox).

        Les bandes restantes restent noires plutôt que d'étirer le rendu.
        """
        display = pygame.display.get_surface()
        size, offset = ui.letterbox(self.screen.get_size(), display.get_size())
        if size == display.get_size():
            display.blit(self.screen, (0, 0))  # la fenêtre a exactement son ratio
        else:
            display.fill((0, 0, 0))  # barres noires
            display.blit(pygame.transform.smoothscale(self.screen, size), offset)
        pygame.display.flip()

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
