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


@pytest.fixture(autouse=True)
def no_gui_dialog(monkeypatch):
    """Neutralise la boîte de dialogue Windows pour toute la suite de tests.

    `MessageBoxW` est modale et sans timeout : sous Windows en CI, personne ne
    peut cliquer « OK », le test se bloque jusqu'au timeout du job (6 h par
    défaut). C'est la panne des runs #6 et #7.
    """
    import main

    monkeypatch.setattr(main, "_show_error_dialog", lambda message: None)
