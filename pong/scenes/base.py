"""Classe de base des scènes.

Une scène représente un écran ou un état du jeu (menu, partie, pause, fin).
L'`App` délègue à la scène courante les événements, la mise à jour et le dessin.
"""


class Scene:
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        """Réagit à un événement pygame (clavier, fermeture de fenêtre...)."""

    def update(self, dt):
        """Met à jour la logique de la scène (dt en secondes)."""

    def draw(self, surface):
        """Dessine la scène sur `surface`."""
