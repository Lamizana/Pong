"""Test de fumée : vérifie le câblage des scènes de bout en bout (sans écran)."""

import pygame

from pong import settings
from pong.app import App
from pong.scenes.game import GameScene
from pong.scenes.gameover import GameOverScene
from pong.scenes.menu import MenuScene
from pong.scenes.pause import PauseScene
from pong.scenes.start import StartScene

def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)

def test_full_scene_flow():
    app = App(sound_enabled=False)
    # Au lancement : l'écran-titre animé.
    assert isinstance(app.scene, StartScene)
    app.scene.handle_event(_key(pygame.K_RETURN))
    assert isinstance(app.scene, MenuScene)

    # Menu → « 1 joueur » (difficulté et points viennent des options).
    target = "1 joueur"
    for _ in range(len(app.scene.options) + 1):
        if app.scene.options[app.scene.index][0] == target:
            break
        app.scene.handle_event(_key(pygame.K_DOWN))
    app.scene.handle_event(_key(pygame.K_RETURN))
    assert isinstance(app.scene, GameScene)
    assert app.scene.mode == "1p"
    assert app.scene.level == app.config["level"]

    # Quelques frames de jeu, sans erreur.
    for _ in range(5):
        app.scene.update(0.016)
        app.scene.draw(app.screen)

    # Pause puis reprise.
    app.scene.handle_event(_key(pygame.K_p))
    assert isinstance(app.scene, PauseScene)
    app.scene.draw(app.screen)
    app.scene.handle_event(_key(pygame.K_p))
    assert isinstance(app.scene, GameScene)

    # Forcer un point : balle sortie à gauche => le camp droit marque.
    game = app.scene
    game.serve_timer = 0.0
    game.ball.x = settings.FIELD_LEFT - game.ball.radius - 10
    game.update(0.016)
    assert game.score.right == 1

    # Forcer la victoire du camp gauche.
    game.score.left = game.points_to_win - 1
    game.serve_timer = 0.0
    game.ball.x = settings.FIELD_RIGHT + game.ball.radius + 10
    game.update(0.016)
    assert isinstance(app.scene, GameOverScene)
    app.scene.draw(app.screen)

    # Retour au menu.
    app.scene.handle_event(_key(pygame.K_m))
    assert isinstance(app.scene, MenuScene)

def test_two_player_mode_has_no_ai():
    app = App(sound_enabled=False)
    app.switch_scene("game", mode="2p")
    assert app.scene.ai is None
    app.scene.update(0.016)
    app.scene.draw(app.screen)

def test_menu_has_expected_entries():
    app = App(sound_enabled=False)
    app.switch_scene("menu")
    labels = [label for label, _, _ in app.scene.options]
    assert labels == ["1 joueur", "2 joueurs", "Options", "Quitter"]
