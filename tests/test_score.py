"""Tests de la logique de score (sans fenêtre graphique)."""

import pytest

from pong.score import Score


def test_new_score_starts_at_zero():
    score = Score()
    assert score.left == 0
    assert score.right == 0
    assert score.winner() is None


def test_left_point_increments_left_only():
    score = Score()
    score.add_point("left")
    assert score.left == 1
    assert score.right == 0


def test_no_winner_before_target():
    score = Score(points_to_win=3)
    score.add_point("left")
    score.add_point("left")
    assert score.winner() is None


def test_reaching_target_declares_winner():
    score = Score(points_to_win=3)
    winner = None
    for _ in range(3):
        winner = score.add_point("left")
    assert winner == "left"
    assert score.winner() == "left"


def test_right_can_win():
    score = Score(points_to_win=2)
    score.add_point("right")
    assert score.add_point("right") == "right"


def test_invalid_side_raises_value_error():
    score = Score()
    with pytest.raises(ValueError):
        score.add_point("middle")


def test_reset_clears_everything():
    score = Score(points_to_win=2)
    score.add_point("left")
    score.add_point("left")
    score.reset()
    assert score.left == 0
    assert score.right == 0
    assert score.winner() is None
