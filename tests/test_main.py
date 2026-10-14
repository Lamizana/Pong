"""Tests du point d'entrée : signalement des erreurs de démarrage."""

import main
from main import report_startup_error


def test_startup_error_is_written_to_log(tmp_path):
    log = report_startup_error("Asset introuvable : /tmp/x.png", log_dir=tmp_path)

    assert log is not None
    assert log.exists()
    assert "Asset introuvable" in log.read_text(encoding="utf-8")


def test_startup_error_shows_the_dialog_through_an_injectable_hook(tmp_path, monkeypatch):
    """La boîte Windows passe par `_show_error_dialog`, jamais un appel direct.

    `MessageBoxW` est modale et sans timeout : appelée en direct sous Windows, elle
    bloquerait la suite de tests (donc la CI) en attendant un clic qui ne viendra
    jamais. Le point d'injection permet de la neutraliser dans les tests.
    """
    shown = []
    monkeypatch.setattr(main, "_show_error_dialog", shown.append)

    report_startup_error("Pong n'a pas pu démarrer", log_dir=tmp_path)

    assert shown == ["Pong n'a pas pu démarrer"]


def test_no_modal_dialog_is_opened_when_running_as_windows(tmp_path, monkeypatch):
    """Garde-fou : même en se faisant passer pour Windows, aucune boîte modale.

    Sans le garde-fou `no_gui_dialog` de conftest, ce test ouvrirait une vraie
    boîte sous Windows et bloquerait la CI (panne des runs #6 et #7).
    """
    import ctypes
    import sys

    opened = []

    class FakeUser32:
        def MessageBoxW(self, *args):  # signature de l'API Windows
            opened.append(args)
            return 1

    class FakeWindll:
        user32 = FakeUser32()

    # ctypes.windll n'existe pas hors Windows : on l'installe pour l'observation.
    monkeypatch.setattr(ctypes, "windll", FakeWindll(), raising=False)
    monkeypatch.setattr(sys, "platform", "win32")

    report_startup_error("Boom", log_dir=tmp_path)

    assert opened == []
