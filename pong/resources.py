"""Chargement des images (assets) du thème.

Les PNG sont produits hors ligne par `scripts/prepare_assets.py` dans
`pong/assets/`. Le chemin est résolu via `__file__`, ce qui fonctionne en
développement comme dans l'exécutable PyInstaller (onefile), où les données
sont extraites à côté du module.
"""

from pathlib import Path

import pygame

from . import settings

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


class AssetStore:
    """Images du jeu, chargées une fois puis réutilisées par les scènes."""

    def __init__(self):
        self.background = self._load_opaque(settings.ASSET_BACKGROUND)
        self.menu_background = self._load_opaque(settings.ASSET_MENU)
        self.menu_frame = self._load_sprite(settings.ASSET_MENU_FRAME)
        self.paddle_left = self._load_sprite(settings.ASSET_PADDLE_LEFT)
        self.paddle_right = self._load_sprite(settings.ASSET_PADDLE_RIGHT)
        self.ball = self._load_sprite(settings.ASSET_BALL)

    @staticmethod
    def _path(name):
        path = ASSETS_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Asset introuvable : {path}")
        return path

    def _load_opaque(self, name):
        """Fond sans transparence, converti au format d'affichage."""
        return pygame.image.load(str(self._path(name))).convert()

    def _load_sprite(self, name):
        """Sprite à transparence, converti au format d'affichage."""
        return pygame.image.load(str(self._path(name))).convert_alpha()
