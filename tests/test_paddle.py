"""Tests du déplacement et des bornes de la raquette."""

import pytest

from pong import settings
from pong.paddle import Paddle


def test_initial_position_is_centered_vertically():
    paddle = Paddle(x=30)
    assert paddle.center_y == pytest.approx((settings.FIELD_TOP + settings.FIELD_BOTTOM) / 2)


def test_move_up_decreases_y_then_down_restores_it():
    paddle = Paddle(x=30)
    start = paddle.y
    paddle.move_up(0.1)
    assert paddle.y < start
    paddle.move_down(0.1)
    assert paddle.y == pytest.approx(start)


def test_cannot_leave_top_of_field():
    paddle = Paddle(x=30)
    paddle.move_up(100)
    assert paddle.y == pytest.approx(settings.FIELD_TOP)


def test_cannot_leave_bottom_of_field():
    paddle = Paddle(x=30)
    paddle.move_down(100)
    assert paddle.y == pytest.approx(settings.FIELD_BOTTOM - paddle.height)


def test_center_y_is_middle_of_paddle():
    paddle = Paddle(x=30)
    assert paddle.center_y == pytest.approx(paddle.y + paddle.height / 2)


def test_rect_matches_position_and_size():
    paddle = Paddle(x=30)
    rect = paddle.rect
    assert rect.x == 30
    assert rect.width == settings.PADDLE_WIDTH
    assert rect.height == settings.PADDLE_HEIGHT


def test_movement_respects_dt_and_speed():
    paddle = Paddle(x=30, speed=100)
    start = paddle.y
    paddle.move_down(0.25)
    assert paddle.y == pytest.approx(start + 25)


def test_move_by_applies_delta_within_bounds():
    paddle = Paddle(x=30)
    start = paddle.y
    paddle.move_by(10)
    assert paddle.y == pytest.approx(start + 10)


def test_move_by_clamps_to_field_bounds():
    paddle = Paddle(x=30)
    paddle.move_by(-1000)
    assert paddle.y == pytest.approx(settings.FIELD_TOP)
    paddle.move_by(100000)
    assert paddle.y == pytest.approx(settings.FIELD_BOTTOM - paddle.height)
