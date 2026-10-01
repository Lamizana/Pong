"""Tests au niveau de la scène de jeu (collisions, sons, décompte)."""

import pygame

from pong import settings
from pong.app import App
from pong.scenes.game import GameScene


class RecordingSound:
    """Double de test : enregistre les sons joués au lieu de les jouer."""

    def __init__(self):
        self.played = []

    def paddle_hit(self):
        self.played.append("hit")

    def wall_bounce(self):
        self.played.append("wall")

    def point_scored(self):
        self.played.append("point")

    def win(self):
        self.played.append("win")


def test_fast_ball_does_not_tunnel_through_left_paddle():
    app = App(sound_enabled=False)
    game = GameScene(app, mode="2p")
    game.serve_timer = 0.0

    ball = game.ball
    ball.y = game.left_paddle.center_y
    ball.x = game.left_paddle.rect.right + ball.radius + 1
    ball.vx = -settings.BALL_MAX_SPEED
    ball.vy = 0.0
    ball.speed = settings.BALL_MAX_SPEED

    # Un pas de temps élevé déplacerait la balle de ~41 px sans sous-pas.
    game.update(0.05)

    assert game.score.left == 0
    assert game.score.right == 0
    assert ball.vx > 0  # la balle est bien repartie vers la droite
    pygame.quit()


def test_win_sound_is_played_on_victory():
    app = App(sound_enabled=False)
    game = GameScene(app, mode="2p")
    app.sound = RecordingSound()
    game.serve_timer = 0.0
    game.score.left = settings.POINTS_TO_WIN - 1
    game.ball.x = settings.WINDOW_WIDTH + game.ball.radius + 10

    game.update(0.016)

    assert "win" in app.sound.played
    pygame.quit()


def test_ai_moves_during_serve_countdown():
    app = App(sound_enabled=False)
    game = GameScene(app, mode="1p", level="difficile")
    game.serve_timer = 1.0
    game.ai.target_offset = 0.0
    game.ball.y = 0.0
    start = game.right_paddle.y

    game.update(0.1)

    assert game.right_paddle.y < start
    pygame.quit()


def test_app_exposes_asset_store():
    from pong.resources import AssetStore

    app = App(sound_enabled=False)
    assert isinstance(app.assets, AssetStore)
    pygame.quit()


def test_game_draw_blits_background_image():
    app = App(sound_enabled=False)
    app.switch_scene("game", mode="2p")
    app.scene.serve_timer = 0.0
    app.scene.draw(app.screen)

    # Coin bas-gauche : seulement le fond, hors raquettes/balle/HUD.
    assert app.screen.get_at((10, 590))[:3] == app.assets.background.get_at((10, 590))[:3]
    pygame.quit()

