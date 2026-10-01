"""La balle : déplacement, rebonds et accélération progressive.

La logique de ce module est pure (hors `pygame.Rect`), donc testable sans fenêtre.
Les positions sont exprimées en pixels, les vitesses en pixels par seconde.
"""

import math
import random

import pygame

from . import settings


class Ball:
    """Une balle de Pong."""

    def __init__(self, x=None, y=None, speed=settings.BALL_START_SPEED):
        self.x = (settings.FIELD_LEFT + settings.FIELD_RIGHT) / 2 if x is None else float(x)
        self.y = (settings.FIELD_TOP + settings.FIELD_BOTTOM) / 2 if y is None else float(y)
        self.radius = settings.BALL_RADIUS
        self.speed = float(speed)
        self.vx = 0.0
        self.vy = 0.0

    @property
    def rect(self):
        """Rectangle de collision (coin haut-gauche + dimensions)."""
        size = self.radius * 2
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), size, size)

    def reset(self, direction=None):
        """Replace la balle au centre et la relance.

        `direction` : +1 vers la droite, -1 vers la gauche (aléatoire si None).
        """
        self.x = (settings.FIELD_LEFT + settings.FIELD_RIGHT) / 2
        self.y = (settings.FIELD_TOP + settings.FIELD_BOTTOM) / 2
        self.speed = settings.BALL_START_SPEED
        if direction is None:
            direction = random.choice((-1, 1))
        angle = math.radians(random.uniform(-30, 30))
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

    def update(self, dt):
        """Avance la balle de `dt` secondes."""
        self.x += self.vx * dt
        self.y += self.vy * dt

    def handle_walls(self):
        """Rebondit sur les bords haut/bas. Renvoie True si un rebond a eu lieu.

        On ne corrige que si la balle se dirige *vers* le mur : évite de « coller »
        une balle immobile (vy == 0) et les doubles rebonds.
        """
        if self.vy < 0 and self.y - self.radius <= settings.FIELD_TOP:
            self.y = settings.FIELD_TOP + self.radius
            self.vy = -self.vy
            return True
        if self.vy > 0 and self.y + self.radius >= settings.FIELD_BOTTOM:
            self.y = settings.FIELD_BOTTOM - self.radius
            self.vy = -self.vy
            return True
        return False

    def bounce_off_paddle(self, paddle_center_y, direction):
        """Rebondit sur une raquette.

        L'angle de sortie dépend de l'écart entre le point d'impact et le centre
        de la raquette : plus la balle frappe près d'un bord, plus l'angle est
        prononcé (borné à MAX_BOUNCE_ANGLE).

        `direction` : +1 pour renvoyer vers la droite, -1 vers la gauche.
        """
        half = settings.PADDLE_HEIGHT / 2
        # offset dans [-1, 1] : -1 = bord haut, 0 = centre, +1 = bord bas
        offset = (self.y - paddle_center_y) / half
        offset = max(-1.0, min(1.0, offset))

        angle = math.radians(settings.MAX_BOUNCE_ANGLE * offset)
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

        # La balle accélère à chaque échange, jusqu'à un maximum.
        self.speed = min(self.speed + settings.BALL_SPEEDUP, settings.BALL_MAX_SPEED)

    def off_screen(self):
        """Renvoie "left" ou "right" si la balle est sortie, sinon None."""
        if self.x + self.radius < settings.FIELD_LEFT:
            return "left"
        if self.x - self.radius > settings.FIELD_RIGHT:
            return "right"
        return None
