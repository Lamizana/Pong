"""Configuration pytest : pilotes SDL factices pour les tests sans écran."""

import os

import pygame
import pytest

# Permet de créer une fenêtre pygame et un mixer audio sans matériel réel.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture(autouse=True)
def pygame_env():
    """Prépare pygame (affichage factice + polices) et le referme après le test.

    L'initialisation est faite ici plutôt que dans chaque test : un test qui
    échoue laisse malgré tout pygame refermé, sans polluer les suivants.
    """
    pygame.display.set_mode((1, 1))
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Isole les réglages persistants : chaque test a son propre dossier."""
    monkeypatch.setenv("PONG_CONFIG_DIR", str(tmp_path / "config"))
