"""Détection de collision cercle / rectangle.

La balle est modélisée par un cercle, la raquette par un `pygame.Rect`. Ces
fonctions sont pures et testables sans écran. Elles remplacent la détection
« boîte englobante » (`Rect.colliderect`), qui rate les contacts sur un coin
lorsque le carré de la balle est seulement tangent à la raquette.
"""

import math


def circle_rect_contact(cx, cy, radius, rect):
    """Contact entre le cercle (cx, cy, radius) et le rectangle `rect`.

    Renvoie `((nx, ny), penetration)` si le cercle touche le rectangle, sinon
    `None`. `(nx, ny)` est la normale unitaire allant du rectangle vers le
    centre du cercle ; `penetration` est la profondeur de chevauchement.
    """
    nearest_x = max(rect.left, min(cx, rect.right))
    nearest_y = max(rect.top, min(cy, rect.bottom))
    dx = cx - nearest_x
    dy = cy - nearest_y
    dist2 = dx * dx + dy * dy
    if dist2 > radius * radius:
        return None
    if dist2 == 0.0:
        # Centre à l'intérieur du rectangle : on repousse vers le haut.
        return (0.0, -1.0), float(radius)
    dist = math.sqrt(dist2)
    return (dx / dist, dy / dist), radius - dist
