"""Tests du point d'entrée : signalement des erreurs de démarrage."""

from main import report_startup_error


def test_startup_error_is_written_to_log(tmp_path):
    log = report_startup_error("Asset introuvable : /tmp/x.png", log_dir=tmp_path)

    assert log is not None
    assert log.exists()
    assert "Asset introuvable" in log.read_text(encoding="utf-8")
