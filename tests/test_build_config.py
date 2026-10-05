"""Tests de packaging : les assets doivent être embarqués dans l'exécutable."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_build_scripts_bundle_assets():
    for name in ("build.sh", "build.ps1", ".github/workflows/build.yml"):
        content = (ROOT / name).read_text(encoding="utf-8")
        assert "pong/assets" in content, f"{name} n'embarque pas pong/assets"


def test_build_scripts_use_os_specific_separator():
    """Le séparateur de --add-data doit être ':' hors Windows et ';' sous Windows."""
    sh = (ROOT / "build.sh").read_text(encoding="utf-8")
    ps1 = (ROOT / "build.ps1").read_text(encoding="utf-8")
    ci = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")

    assert 'pong/assets:pong/assets' in sh
    assert 'pong/assets;pong/assets' in ps1
    assert 'SEP=":"' in ci
    assert 'SEP=";"' in ci
