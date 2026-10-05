"""Test de l'outil d'aperçus : il doit produire les trois écrans."""

from scripts.render_preview import main


def test_render_preview_generates_expected_screens(tmp_path):
    main(str(tmp_path))

    for name in ("menu.png", "game.png", "gameover.png"):
        assert (tmp_path / name).exists(), f"{name} manquant"
