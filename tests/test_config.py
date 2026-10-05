"""Tests de la persistance des réglages (difficulté, points pour gagner)."""

import pygame

from pong import config

def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)

def test_save_then_load_round_trip(tmp_path):
    path = tmp_path / "config.json"

    config.save({"level": "difficile", "points_to_win": 10}, path)

    assert config.load(path) == {"level": "difficile", "points_to_win": 10}

def test_load_returns_defaults_when_file_missing(tmp_path):
    assert config.load(tmp_path / "absent.json") == config.DEFAULTS

def test_load_returns_defaults_on_corrupt_file(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{ ceci n'est pas du json", encoding="utf-8")

    assert config.load(path) == config.DEFAULTS

def test_load_ignores_invalid_values(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"level": "impossible", "points_to_win": 42}', encoding="utf-8")

    assert config.load(path) == config.DEFAULTS

def test_save_failure_is_silent(tmp_path):
    """Un dossier de configuration non inscriptible ne doit pas planter le jeu."""
    blocker = tmp_path / "fichier"
    blocker.write_text("x", encoding="utf-8")

    assert config.save(config.DEFAULTS, blocker / "config.json") is False

def test_options_change_is_persisted(monkeypatch):
    from pong.app import App

    saved = []
    monkeypatch.setattr(config, "save", lambda cfg: saved.append(dict(cfg)))

    app = App(sound_enabled=False)
    app.switch_scene("options")
    app.scene.index = 0  # ligne « Difficulté »
    app.scene.handle_event(_key(pygame.K_RIGHT))

    assert saved, "le changement de réglage n'a pas été enregistré"
    assert saved[-1]["level"] == app.config["level"]
