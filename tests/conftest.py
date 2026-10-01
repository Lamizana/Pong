"""Configuration pytest : pilotes SDL factices pour les tests sans écran."""

import os

# Permet de créer une fenêtre pygame et un mixer audio sans matériel réel.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
