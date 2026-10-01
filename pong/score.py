"""Gestion du score et de la condition de victoire.

Logique pure : ce module ne dépend pas de pygame et se teste sans fenêtre.
"""

from .settings import POINTS_TO_WIN


class Score:
    """Compte les points des deux camps et détecte la victoire.

    `side` vaut "left" (joueur 1) ou "right" (joueur 2 / IA).
    """

    def __init__(self, points_to_win=POINTS_TO_WIN):
        self.points_to_win = points_to_win
        self.reset()

    def reset(self):
        """Remet les deux scores à zéro."""
        self.left = 0
        self.right = 0

    def add_point(self, side):
        """Ajoute un point à `side` et renvoie le vainqueur, ou None."""
        if side == "left":
            self.left += 1
        elif side == "right":
            self.right += 1
        else:
            raise ValueError(f"côté invalide : {side!r} (attendu 'left' ou 'right')")
        return self.winner()

    def winner(self):
        """Renvoie "left", "right", ou None si la partie continue."""
        if self.left >= self.points_to_win:
            return "left"
        if self.right >= self.points_to_win:
            return "right"
        return None
