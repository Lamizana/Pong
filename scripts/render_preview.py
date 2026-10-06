"""Génère des aperçus PNG des écrans du jeu (README, tutoriel, CI).

Usage : python scripts/render_preview.py [dossier_de_sortie]
Défaut : docs/screenshots
"""

import os
import sys

# Rendu sans écran ni carte son.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Permet d'importer le package `pong` quel que soit le dossier courant.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from pong.app import App  # noqa: E402
from pong.scenes.gameover import GameOverScene  # noqa: E402


def main(out_dir="docs/screenshots"):
    os.makedirs(out_dir, exist_ok=True)
    app = App(sound_enabled=False)

    # Écran-titre « PRESS START » (scène d'ouverture).
    app.scene.draw(app.screen)
    pygame.image.save(app.screen, os.path.join(out_dir, "start.png"))

    # Menu principal.
    app.switch_scene("menu")
    app.scene.draw(app.screen)
    pygame.image.save(app.screen, os.path.join(out_dir, "menu.png"))

    # Partie en cours (2 joueurs).
    app.switch_scene("game", mode="2p")
    game = app.scene
    game.serve_timer = 0.0
    game.ball.x, game.ball.y = 400, 220
    game.score.left, game.score.right = 3, 5
    game.right_paddle.y = 120
    game.draw(app.screen)
    pygame.image.save(app.screen, os.path.join(out_dir, "game.png"))

    # Écran de fin de partie.
    app.set_scene(GameOverScene(app, "left", "1p"))
    app.scene.draw(app.screen)
    pygame.image.save(app.screen, os.path.join(out_dir, "gameover.png"))

    pygame.quit()
    print(f"Aperçus enregistrés dans {out_dir}/ "
          f"(start.png, menu.png, game.png, gameover.png)")


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
