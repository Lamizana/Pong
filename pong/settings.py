"""Constantes globales du jeu.

Ce module ne contient aucune logique : uniquement des valeurs de configuration,
regroupées ici pour être ajustées en un seul endroit.
"""

import pygame

# --- Fenêtre ---
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FPS = 60
CAPTION = "Pong"

# --- Couleurs (RVB) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)
ACCENT = (0, 200, 255)
GREEN = (80, 220, 120)
RED = (230, 90, 90)

# --- Raquette ---
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_MARGIN = 30          # distance entre la raquette et le bord
PADDLE_SPEED = 520          # pixels par seconde

# --- Balle ---
BALL_RADIUS = 8
BALL_START_SPEED = 360      # pixels par seconde
BALL_SPEEDUP = 22           # gain de vitesse à chaque échange
BALL_MAX_SPEED = 820
MAX_BOUNCE_ANGLE = 60       # angle maximal de rebond, en degrés

# --- Score ---
POINTS_TO_WIN = 7

# --- Contrôles (touches pygame) ---
# Joueur 1 : Z/S (AZERTY) et W/S (QWERTY) en secours.
P1_UP = (pygame.K_z, pygame.K_w)
P1_DOWN = (pygame.K_s,)
# Joueur 2 : flèches haut / bas.
P2_UP = (pygame.K_UP,)
P2_DOWN = (pygame.K_DOWN,)
# Navigation / actions.
KEY_PAUSE = (pygame.K_p, pygame.K_ESCAPE)
KEY_VALIDATE = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
KEY_MENU = (pygame.K_q, pygame.K_m)

# --- IA : réglages ---
AI_DEAD_ZONE = 6            # tolérance (px) autour de la cible, évite le tremblement

# --- IA : niveaux de difficulté ---
# speed : vitesse maximale de la raquette de l'IA (px/s)
# error : écart maximal (px) visé par rapport au centre de la balle (rend l'IA battable)
AI_LEVELS = {
    "facile": {"speed": 300, "error": 70, "label": "1 joueur — Facile"},
    "moyen": {"speed": 440, "error": 35, "label": "1 joueur — Moyen"},
    "difficile": {"speed": 640, "error": 8, "label": "1 joueur — Difficile"},
}

# --- Sons ---
SOUND_SAMPLE_RATE = 44100
SOUND_VOLUME = 0.4
SOUND_HIT_FREQ = 440
SOUND_WALL_FREQ = 300
SOUND_SCORE_FREQ = 200
SOUND_WIN_FREQ = 660
SOUND_DURATION_MS = 90
