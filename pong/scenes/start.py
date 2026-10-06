"""Écran-titre : la vidéo d'accueil tourne en boucle, toute touche passe au menu."""

import pygame

from .. import settings
from ..resources import video_frames
from .base import Scene

# Nombre de frames gardées en mémoire autour de la frame courante.
_CACHE_WINDOW = 3


class StartScene(Scene):
    """Joue l'animation d'accueil en boucle, avec sa musique de fond."""

    def __init__(self, app):
        super().__init__(app)
        self.time = 0.0
        self._cache = {}
        try:
            self.frames = video_frames(settings.ASSET_START_VIDEO)
        except FileNotFoundError:
            # Repli : image statique si les frames n'ont pas été générées.
            self.frames = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.app.switch_scene("menu")

    def update(self, dt):
        self.time += dt
        if self.frames:
            self._fill_cache()

    def _index(self):
        """Index de la frame courante : la boucle revient à 0 en fin d'animation."""
        return int(self.time * settings.START_VIDEO_FPS) % len(self.frames)

    def _fill_cache(self):
        """Charge la frame courante et les suivantes, une seule par image.

        Décoder une JPEG n'est pas instantané : en répartissant les chargements
        sur plusieurs images affichées, la lecture reste fluide.
        """
        count = len(self.frames)
        index = self._index()
        for offset in range(_CACHE_WINDOW + 1):
            i = (index + offset) % count
            if i not in self._cache:
                self._cache[i] = pygame.image.load(str(self.frames[i])).convert()
                break
        keep = {(index + offset) % count for offset in range(-1, _CACHE_WINDOW + 1)}
        for i in [i for i in self._cache if i not in keep]:
            del self._cache[i]

    def draw(self, surface):
        if not self.frames:
            surface.blit(self.app.assets.start_screen, (0, 0))
            return
        frame = self._cache.get(self._index())
        surface.blit(frame if frame is not None else self.app.assets.start_screen, (0, 0))
