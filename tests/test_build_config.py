"""Tests de packaging : les assets doivent être embarqués dans l'exécutable."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_build_scripts_bundle_assets():
    for name in ("build.sh", "build.ps1", ".github/workflows/build.yml"):
        content = (ROOT / name).read_text(encoding="utf-8")
        assert "pong/assets" in content, f"{name} n'embarque pas pong/assets"
