"""L'IA : pilote une raquette pour affronter le joueur en mode 1 joueur.

La difficulté règle deux paramètres : la vitesse maximale de la raquette et
l'imprécision de la visée (`error`). Une visée décalée rend l'IA battable même
lorsqu'elle pourrait suivre parfaitement la balle.

Logique pure : testable sans fenêtre ni boucle de jeu.
"""

import random

from . import settings


class AI:
    """Un adversaire automatique contrôlant une raquette."""

    def __init__(self, level="moyen", rng=None):
        if level not in settings.AI_LEVELS:
            raise ValueError(f"niveau inconnu : {level!r}")
        config = settings.AI_LEVELS[level]
        self.level = level
        self.speed = config["speed"]
        self.error = config["error"]
        self._rng = rng or random.Random()
        self.target_offset = 0.0

    def randomize_offset(self):
        """Tire une nouvelle imprécision de visée (à chaque nouvel échange)."""
        self.target_offset = self._rng.uniform(-self.error, self.error)

    def update(self, ball_y, paddle, dt):
        """Déplace `paddle` vers la balle, sans dépasser la vitesse du niveau."""
        target = ball_y + self.target_offset
        diff = target - paddle.center_y
        if abs(diff) <= settings.AI_DEAD_ZONE:
            return  # assez proche : on ne bouge pas (évite le tremblement)
        direction = 1 if diff > 0 else -1
        step = min(abs(diff), self.speed * dt)
        paddle.move_by(direction * step)
