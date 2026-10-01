"""Tests de la physique de la balle (sans fenêtre graphique)."""

import math

import pytest

from pong import settings
from pong.ball import Ball


# --- Mise en place / remise en jeu ---

def test_reset_centers_ball_and_restores_start_speed():
    ball = Ball()
    ball.reset(direction=1)
    assert ball.x == pytest.approx(settings.WINDOW_WIDTH / 2)
    assert ball.y == pytest.approx(settings.WINDOW_HEIGHT / 2)
    assert ball.speed == pytest.approx(settings.BALL_START_SPEED)
    assert ball.vx > 0


def test_reset_direction_left_gives_negative_vx():
    ball = Ball()
    ball.reset(direction=-1)
    assert ball.vx < 0


# --- Déplacement ---

def test_update_moves_according_to_velocity():
    ball = Ball()
    ball.x, ball.y = 100.0, 100.0
    ball.vx, ball.vy = 60.0, -30.0
    ball.update(0.5)
    assert ball.x == pytest.approx(130.0)
    assert ball.y == pytest.approx(85.0)


# --- Rebond sur les murs haut / bas ---

def test_bounce_off_top_wall():
    ball = Ball()
    ball.y = settings.BALL_RADIUS - 1
    ball.vy = -200.0
    bounced = ball.handle_walls()
    assert bounced is True
    assert ball.vy > 0
    assert ball.y == pytest.approx(settings.BALL_RADIUS)


def test_bounce_off_bottom_wall():
    ball = Ball()
    ball.y = settings.WINDOW_HEIGHT - settings.BALL_RADIUS + 1
    ball.vy = 200.0
    bounced = ball.handle_walls()
    assert bounced is True
    assert ball.vy < 0


def test_no_wall_bounce_in_middle():
    ball = Ball()
    assert ball.handle_walls() is False


# --- Rebond sur une raquette (angle selon le point d'impact) ---

def test_hit_paddle_center_goes_straight():
    ball = Ball()
    ball.y = 300.0
    ball.bounce_off_paddle(paddle_center_y=300.0, direction=1)
    assert ball.vy == pytest.approx(0.0, abs=1e-6)
    assert ball.vx == pytest.approx(settings.BALL_START_SPEED)


def test_hit_paddle_top_sends_ball_upward():
    ball = Ball()
    center = 300.0
    ball.y = center - settings.PADDLE_HEIGHT / 2
    ball.bounce_off_paddle(paddle_center_y=center, direction=1)
    assert ball.vy < 0
    assert ball.vx > 0


def test_hit_paddle_bottom_sends_ball_downward():
    ball = Ball()
    center = 300.0
    ball.y = center + settings.PADDLE_HEIGHT / 2
    ball.bounce_off_paddle(paddle_center_y=center, direction=1)
    assert ball.vy > 0


def test_hit_left_paddle_sends_ball_right():
    ball = Ball()
    ball.bounce_off_paddle(paddle_center_y=300.0, direction=1)
    assert ball.vx > 0


def test_hit_right_paddle_sends_ball_left():
    ball = Ball()
    ball.bounce_off_paddle(paddle_center_y=300.0, direction=-1)
    assert ball.vx < 0


def test_max_bounce_angle_is_clamped():
    ball = Ball()
    ball.y = 300.0 - 5000  # très au-dessus du centre : l'angle doit être borné
    ball.bounce_off_paddle(paddle_center_y=300.0, direction=1)
    angle = math.degrees(math.atan2(abs(ball.vy), abs(ball.vx)))
    assert angle == pytest.approx(settings.MAX_BOUNCE_ANGLE, abs=0.5)


# --- Accélération progressive ---

def test_each_hit_speeds_ball_up():
    ball = Ball()
    ball.bounce_off_paddle(paddle_center_y=300.0, direction=1)
    assert ball.speed == pytest.approx(settings.BALL_START_SPEED + settings.BALL_SPEEDUP)


def test_speed_is_capped_at_maximum():
    ball = Ball(speed=settings.BALL_MAX_SPEED)
    ball.bounce_off_paddle(paddle_center_y=300.0, direction=1)
    assert ball.speed == pytest.approx(settings.BALL_MAX_SPEED)


# --- Sortie de terrain ---

def test_off_screen_left_and_right():
    ball = Ball()
    ball.x = -ball.radius - 1
    assert ball.off_screen() == "left"
    ball.x = settings.WINDOW_WIDTH + ball.radius + 1
    assert ball.off_screen() == "right"
    ball.x = settings.WINDOW_WIDTH / 2
    assert ball.off_screen() is None


# --- Cas limites sur les murs ---

def test_no_bounce_when_vy_is_zero():
    ball = Ball()
    ball.y = settings.BALL_RADIUS - 1
    ball.vy = 0.0
    assert ball.handle_walls() is False


def test_no_bounce_when_already_moving_away_from_top():
    ball = Ball()
    ball.y = settings.BALL_RADIUS - 1
    ball.vy = 100.0  # déjà orientée vers le bas
    assert ball.handle_walls() is False

