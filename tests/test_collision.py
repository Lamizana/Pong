"""Tests de la détection de collision cercle / rectangle (pure)."""

import pygame

from pong.collision import circle_rect_contact


def _rect():
    return pygame.Rect(100, 100, 15, 80)


def test_contact_on_side_face():
    contact = circle_rect_contact(93.0, 140.0, 8, _rect())
    assert contact is not None
    (nx, ny), penetration = contact
    assert nx < 0 and abs(ny) < 1e-6
    assert penetration == 1.0


def test_contact_detected_on_corner_where_bounding_box_misses():
    # Cœur du bug corrigé : le carré englobant de la balle a son bord inférieur
    # tout juste sur le bord supérieur de la raquette (donc `colliderect` = faux),
    # mais le cercle réel touche bien le coin supérieur.
    rect = _rect()
    cx, cy, radius = 107.0, 92.05, 8.0
    assert int(cy - radius) + 2 * radius <= rect.top  # le carré ne touche pas

    contact = circle_rect_contact(cx, cy, radius, rect)

    assert contact is not None
    (nx, ny), penetration = contact
    assert ny < 0
    assert 0 < penetration <= radius


def test_tangent_counts_as_contact():
    assert circle_rect_contact(107.0, 92.0, 8, _rect()) is not None


def test_no_contact_when_clearly_far():
    assert circle_rect_contact(107.0, 88.0, 8, _rect()) is None
