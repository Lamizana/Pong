"""Helpers d'interface partagés par les écrans à panneau (menu, options, fin)."""

import pygame

from . import neon, settings

# Zone verticale du panneau où loger les lignes (fractions de sa hauteur).
ZONE_TOP = 0.26
ZONE_BOTTOM = 0.74


def fit_menu_frame(frame):
    """Réduit le cadre du menu pour qu'il tienne dans le rectangle bleu néon."""
    width = settings.FIELD_WIDTH - 40
    height = max(1, round(frame.get_height() * width / frame.get_width()))
    return pygame.transform.smoothscale(frame, (width, height))


def panel_rect(frame):
    """Rectangle du panneau : centré sur le terrain du décor."""
    return frame.get_rect(center=(
        (settings.FIELD_LEFT + settings.FIELD_RIGHT) // 2,
        (settings.FIELD_TOP + settings.FIELD_BOTTOM) // 2))


def navigation_index(event, index, count):
    """Nouvel index de sélection, ou None si l'événement n'est pas un déplacement.

    Flèches haut/bas et Z/S/W (mêmes touches que les raquettes), avec bouclage.
    """
    if event.type != pygame.KEYDOWN:
        return None
    if event.key in settings.P1_UP or event.key in settings.P2_UP:
        return (index - 1) % count
    if event.key in settings.P1_DOWN or event.key in settings.P2_DOWN:
        return (index + 1) % count
    return None


def draw_choices(surface, app, frame_rect, labels, index, spread=1,
                 zone_top=ZONE_TOP, zone_bottom=ZONE_BOTTOM):
    """Dessine les choix dans une zone verticale du panneau (texte clair).

    La sélection est en rose néon, précédée de « > », avec un halo discret.
    """
    top = frame_rect.top + int(zone_top * frame_rect.height)
    bottom = frame_rect.top + int(zone_bottom * frame_rect.height)
    spacing = max(1, (bottom - top) // len(labels))
    first_y = top + spacing // 2
    for i, label in enumerate(labels):
        selected = i == index
        text = ("> " if selected else "  ") + label
        color = settings.NEON_PINK if selected else settings.TEXT_DIM
        center = (settings.WINDOW_WIDTH // 2, first_y + i * spacing)
        if selected:
            neon.glow_text(surface, app.font_small, text, color, center=center, spread=spread)
        else:
            app.draw_text(surface, text, app.font_small, color, center=center)


def hint_y(app):
    """Ordonnée du centre de l'invite, calée sur la hauteur de la police."""
    return settings.WINDOW_HEIGHT - app.font_small.get_height()


def stacked_centers(center_y, heights, gap=16):
    """Centres verticaux d'un bloc de textes empilés, centré sur `center_y`."""
    total = sum(heights) + gap * (len(heights) - 1)
    y = center_y - total // 2
    centers = []
    for height in heights:
        centers.append(y + height // 2)
        y += height + gap
    return centers


def draw_hint(surface, app, text):
    """Invite affichée en bas de la fenêtre."""
    app.draw_text(surface, text, app.font_small, settings.TEXT_DIM,
                  center=(settings.WINDOW_WIDTH // 2, hint_y(app)))
