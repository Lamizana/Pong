"""Tests au niveau de la scène de jeu (collisions, sons, décompte)."""

import pygame

from pong import settings
from pong.app import App
from pong.scenes.game import GameScene
from pong.scenes.gameover import GameOverScene

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

def test_win_sound_is_played_on_victory():
    app = App(sound_enabled=False)
    game = GameScene(app, mode="2p")
    app.sound = RecordingSound()
    game.serve_timer = 0.0
    game.score.left = game.points_to_win - 1
    game.ball.x = settings.FIELD_RIGHT + game.ball.radius + 10

    game.update(0.016)

    assert "win" in app.sound.played

def test_ai_moves_during_serve_countdown():
    app = App(sound_enabled=False)
    app.config["level"] = "difficile"
    game = GameScene(app, mode="1p")
    game.serve_timer = 1.0
    game.ai.target_offset = 0.0
    game.ball.y = 0.0
    start = game.right_paddle.y

    game.update(0.1)

    assert game.right_paddle.y < start

def test_app_exposes_asset_store():
    from pong.resources import AssetStore

    app = App(sound_enabled=False)
    assert isinstance(app.assets, AssetStore)

def test_game_draw_blits_background_image():
    app = App(sound_enabled=False)
    app.switch_scene("game", mode="2p")
    app.scene.serve_timer = 0.0
    app.scene.draw(app.screen)

    # Coin bas-gauche : seulement le fond, hors raquettes/balle/HUD.
    assert app.screen.get_at((10, 590))[:3] == app.assets.background.get_at((10, 590))[:3]

def test_ball_spins_while_moving():
    """La balle tourne sur elle-même quand elle se déplace."""
    app = App(sound_enabled=False)
    game = GameScene(app, mode="2p")
    game.serve_timer = 0.0
    game.ball.vx = 300.0
    before = game.ball_angle

    game.update(0.1)

    assert game.ball_angle != before
    game.draw(app.screen)  # le sprite pivoté se dessine sans erreur

def test_ball_bounces_when_touching_paddle_corner():
    """Régression : le carré englobant de la balle rate le coin supérieur
    (bord tangent), alors que son cercle touche la raquette. La balle doit
    rebondir au lieu de traverser."""
    app = App(sound_enabled=False)
    game = GameScene(app, mode="2p")
    game.serve_timer = 0.0
    paddle = game.left_paddle
    ball = game.ball
    # Cercle chevauchant le coin supérieur gauche, carré englobant à l'extérieur.
    ball.x = paddle.rect.left
    ball.y = paddle.rect.top - ball.radius + 0.5
    ball.vx, ball.vy = -100.0, 0.0
    ball.speed = 100.0

    game.update(0.001)

    assert ball.vx > 0, "la balle a traversé la raquette sur un coin"

def test_game_uses_configured_points_to_win():
    """La partie se gagne aux points réglés dans les options."""
    app = App(sound_enabled=False)
    app.config["points_to_win"] = 3
    app.switch_scene("game", mode="2p")
    game = app.scene
    game.serve_timer = 0.0
    game.score.left = 2  # un point de plus et c'est la victoire
    game.ball.x = settings.FIELD_RIGHT + game.ball.radius + 10

    game.update(0.016)

    assert isinstance(app.scene, GameOverScene)

def test_paddle_sprites_stay_inside_the_field():
    """Les sprites de raquettes tiennent dans le terrain délimité par FIELD_*."""
    app = App(sound_enabled=False)
    game = GameScene(app, mode="2p")
    left_sprite = app.assets.paddle_left.get_width()
    right_sprite = app.assets.paddle_right.get_width()

    assert game.left_paddle.rect.right - left_sprite >= settings.FIELD_LEFT
    assert game.left_paddle.rect.right <= settings.FIELD_RIGHT
    assert game.right_paddle.rect.left >= settings.FIELD_LEFT
    assert game.right_paddle.rect.left + right_sprite <= settings.FIELD_RIGHT

def test_left_paddle_sprite_face_touches_collision_rect():
    """Le bord intérieur du sprite gauche coïncide avec le Rect de collision."""
    app = App(sound_enabled=False)
    game = GameScene(app, mode="2p")
    # Fond uni : seuls les pixels de la raquette seront peints.
    background = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    background.fill((0, 0, 0))
    app.assets.background = background

    game.draw(app.screen)

    rect = game.left_paddle.rect
    painted = [x for x in range(rect.right - 60, rect.right + 8)
               if app.screen.get_at((x, rect.centery))[:3] != (0, 0, 0)]
    assert painted, "aucun pixel de raquette dessiné"
    assert max(painted) <= rect.right - 1
    assert max(painted) >= rect.right - 4

