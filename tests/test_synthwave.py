"""Tests des calculs purs du décor synthwave (géométrie, étoiles, pulsation)."""

from pong.synthwave import (
    generate_stars,
    horizontal_grid_ys,
    lerp_color,
    sun_pulse,
    vertical_grid_segments,
)


def test_lerp_color_endpoints():
    assert lerp_color((0, 0, 0), (255, 255, 255), 0.0) == (0, 0, 0)
    assert lerp_color((0, 0, 0), (255, 255, 255), 1.0) == (255, 255, 255)


def test_lerp_color_midpoint():
    assert lerp_color((0, 0, 0), (100, 200, 50), 0.5) == (50, 100, 25)


def test_horizontal_grid_ys_increasing_and_bounded():
    ys = horizontal_grid_ys(horizon_y=300, height=600, count=12)
    assert len(ys) == 12
    assert ys == sorted(ys)
    assert all(300 < y <= 600 for y in ys)
    # Perspective : l'espacement augmente quand on s'approche du bas.
    spacings = [b - a for a, b in zip(ys, ys[1:])]
    assert spacings == sorted(spacings)


def test_vertical_grid_segments_span_horizon_to_bottom():
    segments = vertical_grid_segments(cx=450, horizon_y=300, width=900, height=600, spacing=90)
    assert segments
    for (x1, y1), (x2, y2) in segments:
        assert y1 == 300
        assert y2 == 600
    bottom_xs = [x2 for (_, _), (x2, _) in segments]
    assert any(x < 450 for x in bottom_xs)
    assert any(x > 450 for x in bottom_xs)


def test_generate_stars_is_deterministic_and_bounded():
    stars_a = generate_stars(40, width=900, sky_height=300, seed=1)
    stars_b = generate_stars(40, width=900, sky_height=300, seed=1)
    assert stars_a == stars_b
    assert len(stars_a) == 40
    for x, y, brightness in stars_a:
        assert 0 <= x <= 900
        assert 0 <= y <= 300
        assert 0.0 <= brightness <= 1.0


def test_sun_pulse_stays_near_one():
    for step in range(20):
        value = sun_pulse(step * 0.37)
        assert 0.9 <= value <= 1.1
