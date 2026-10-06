"""Chargement des assets (images et police) du thème.

Les fichiers sont produits hors ligne par `scripts/prepare_assets.py` (images)
et embarqués dans `pong/assets/`. Le chemin est résolu via `__file__`, ce qui
fonctionne en développement comme dans l'exécutable PyInstaller (onefile), où
les données sont extraites à côté du module.
"""

from pathlib import Path

import pygame

from . import settings

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def asset_path(name):
    """Chemin absolu d'un asset, avec une erreur claire s'il est absent."""
    path = ASSETS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Asset introuvable : {path}")
    return path


class AssetStore:
    """Images du jeu, chargées une fois puis réutilisées par les scènes."""

    def __init__(self):
        self.background = self._load_opaque(settings.ASSET_BACKGROUND)
        self.start_screen = self._load_opaque(settings.ASSET_START)
        self.menu_background = self._load_opaque(settings.ASSET_MENU)
        self.menu_frame = self._load_sprite(settings.ASSET_MENU_FRAME)
        self.title = self._load_sprite(settings.ASSET_TITLE)
        self.score_screen = self._load_sprite(settings.ASSET_SCORE_SCREEN)
        self.paddle_left = self._load_sprite(settings.ASSET_PADDLE_LEFT)
        self.paddle_right = self._load_sprite(settings.ASSET_PADDLE_RIGHT)
        self.ball = self._load_sprite(settings.ASSET_BALL)

    @staticmethod
    def _load_opaque(name):
        """Fond sans transparence, converti au format d'affichage."""
        return pygame.image.load(str(asset_path(name))).convert()

    @staticmethod
    def _load_sprite(name):
        """Sprite à transparence, converti au format d'affichage."""
        return pygame.image.load(str(asset_path(name))).convert_alpha()
