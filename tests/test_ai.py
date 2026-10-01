"""Tests de la logique de l'IA (décision de déplacement)."""

import random

import pytest

from pong import settings
from pong.ai import AI
from pong.paddle import Paddle


def test_unknown_level_raises_value_error():
    with pytest.raises(ValueError):
        AI(level="impossible")


def test_levels_get_faster_and_more_precise():
    easy = settings.AI_LEVELS["facile"]
    medium = settings.AI_LEVELS["moyen"]
    hard = settings.AI_LEVELS["difficile"]
    assert easy["speed"] < medium["speed"] < hard["speed"]
    assert easy["error"] > medium["error"] > hard["error"]


def test_moves_down_when_target_is_below():
    ai = AI(level="moyen")
    ai.target_offset = 0.0
    paddle = Paddle(x=30)
    paddle.y = 100
    ai.update(ball_y=300, paddle=paddle, dt=0.1)
    assert paddle.y > 100


def test_moves_up_when_target_is_above():
    ai = AI(level="moyen")
    ai.target_offset = 0.0
    paddle = Paddle(x=30)
    paddle.y = 400
    ai.update(ball_y=200, paddle=paddle, dt=0.1)
    assert paddle.y < 400


def test_does_not_move_inside_dead_zone():
    ai = AI(level="difficile")
    ai.target_offset = 0.0
    paddle = Paddle(x=30)
    start = paddle.y
    ai.update(ball_y=paddle.center_y + 2, paddle=paddle, dt=0.1)
    assert paddle.y == pytest.approx(start)


def test_step_is_limited_by_ai_speed():
    ai = AI(level="facile")
    paddle = Paddle(x=30)
    paddle.y = settings.FIELD_TOP
    ai.update(ball_y=100000, paddle=paddle, dt=0.1)
    assert paddle.y - settings.FIELD_TOP <= ai.speed * 0.1 + 1e-6


def test_offset_shifts_the_aim():
    ai = AI(level="moyen")
    ai.target_offset = 100.0
    paddle = Paddle(x=30)
    start = paddle.y
    # balle au centre, mais visée décalée vers le bas
    ai.update(ball_y=paddle.center_y, paddle=paddle, dt=0.1)
    assert paddle.y > start


def test_randomize_offset_stays_within_error():
    ai = AI(level="facile", rng=random.Random(42))
    for _ in range(50):
        ai.randomize_offset()
        assert abs(ai.target_offset) <= ai.error
