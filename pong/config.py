"""Réglages persistants (difficulté, points pour gagner).

Enregistrés en JSON dans le dossier de configuration de l'utilisateur :

- `PONG_CONFIG_DIR` s'il est défini (pratique pour les tests) ;
- `%APPDATA%/Pong` sous Windows ;
- `$XDG_CONFIG_HOME/pong` ou `~/.config/pong` ailleurs.
"""

import json
import os
import sys
from pathlib import Path

from . import settings

DEFAULTS = {
    "level": "moyen",
    "points_to_win": settings.POINTS_TO_WIN,
}


def config_dir():
    """Dossier de configuration selon le système."""
    override = os.environ.get("PONG_CONFIG_DIR")
    if override:
        return Path(override)
    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        return Path(base) / "Pong" if base else Path.home() / "AppData" / "Roaming" / "Pong"
    base = os.environ.get("XDG_CONFIG_HOME")
    return Path(base) / "pong" if base else Path.home() / ".config" / "pong"


def config_path():
    """Chemin du fichier de configuration."""
    return config_dir() / "config.json"


def load(path=None):
    """Réglages enregistrés, complétés et validés par les valeurs par défaut.

    Un fichier absent, illisible ou corrompu, ou des valeurs hors des choix
    proposés, retombent silencieusement sur les valeurs par défaut.
    """
    path = Path(path) if path else config_path()
    config = dict(DEFAULTS)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return config
    if not isinstance(data, dict):
        return config
    if data.get("level") in settings.AI_LEVELS:
        config["level"] = data["level"]
    if data.get("points_to_win") in settings.POINT_CHOICES:
        config["points_to_win"] = data["points_to_win"]
    return config


def save(config, path=None):
    """Écrit les réglages ; renvoie False si l'écriture est impossible.

    Un échec d'écriture (dossier protégé, disque plein) ne doit jamais
    interrompre une partie : on l'ignore.
    """
    path = Path(path) if path else config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return False
    return True
