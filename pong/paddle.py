"""La raquette : déplacement borné à l'écran.

Positions en pixels, vitesse en pixels par seconde. Logique pure, testable
sans fenêtre (seul `pygame.Rect` est utilisé).
"""

import pygame

from . import settings


class Paddle:
    """Une raquette verticale contrôlée par un joueur ou par l'IA."""

    def __init__(self, x, speed=settings.PADDLE_SPEED, height=settings.PADDLE_HEIGHT):
        self.width = settings.PADDLE_WIDTH
        self.height = height
        self.speed = float(speed)
        self.x = float(x)
        self.y = (settings.WINDOW_HEIGHT - height) / 2

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def center_y(self):
        return self.y + self.height / 2

    def reset(self):
        """Replace la raquette au centre vertical."""
        self.y = (settings.WINDOW_HEIGHT - self.height) / 2

    def move(self, direction, dt):
        """Déplace la raquette de `direction` (-1 haut, +1 bas) sur `dt` secondes."""
        self.move_by(direction * self.speed * dt)

    def move_by(self, delta):
        """Déplace la raquette de `delta` pixels, en la gardant à l'écran."""
        self.y += delta
        # Bornes : on empêche la raquette de sortir de l'écran.
        self.y = max(0.0, min(self.y, settings.WINDOW_HEIGHT - self.height))

    def move_up(self, dt):
        self.move(-1, dt)

    def move_down(self, dt):
        self.move(1, dt)
