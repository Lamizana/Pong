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

# --- Terrain de jeu (cadre bleu néon du décor) ---
# Le rectangle lumineux du fond délimite la zone de jeu réelle.
FIELD_LEFT = 80
FIELD_RIGHT = 820
FIELD_TOP = 92
FIELD_BOTTOM = 512
FIELD_WIDTH = FIELD_RIGHT - FIELD_LEFT
FIELD_HEIGHT = FIELD_BOTTOM - FIELD_TOP

# --- Raquette ---
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
PADDLE_INSET = 4            # écart entre le bord du terrain et le sprite
PADDLE_SPEED = 520          # pixels par seconde

# --- Balle ---
BALL_RADIUS = 8
BALL_START_SPEED = 360      # pixels par seconde
BALL_SPEEDUP = 22           # gain de vitesse à chaque échange
BALL_MAX_SPEED = 820
MAX_BOUNCE_ANGLE = 60       # angle maximal de rebond, en degrés
BALL_SPIN_FACTOR = 0.2      # vitesse de rotation visuelle de la balle (réglable)

# --- Score ---
POINTS_TO_WIN = 5
POINT_CHOICES = (3, 5, 10)  # valeurs proposées dans les options

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

# --- Polices (Orbitron, embarquée dans pong/assets/) ---
FONT_SMALL_SIZE = 28
FONT_MEDIUM_SIZE = 44
FONT_LARGE_SIZE = 72

# --- IA : réglages ---
AI_DEAD_ZONE = 6            # tolérance (px) autour de la cible, évite le tremblement

# --- IA : niveaux de difficulté ---
# speed : vitesse maximale de la raquette de l'IA (px/s)
# error : écart maximal (px) visé par rapport au centre de la balle (rend l'IA battable)
AI_LEVELS = {
    "facile": {"speed": 300, "error": 70, "label": "Facile"},
    "moyen": {"speed": 440, "error": 35, "label": "Moyen"},
    "difficile": {"speed": 640, "error": 8, "label": "Difficile"},
}

# --- Sons ---
SOUND_SAMPLE_RATE = 44100
SOUND_VOLUME = 0.4
SOUND_HIT_FREQ = 440
SOUND_WALL_FREQ = 300
SOUND_SCORE_FREQ = 200
SOUND_WIN_FREQ = 660
SOUND_DURATION_MS = 90

# --- Interface ---
OVERLAY_COLOR = (18, 6, 46)     # voile sombre par-dessus le jeu (pause)

# Couleurs néon
NEON_PINK = (255, 45, 149)
NEON_CYAN = (0, 229, 255)
NEON_YELLOW = (255, 214, 102)
TEXT_COLOR = (236, 226, 255)
TEXT_DIM = (188, 172, 224)

# --- Assets (images du thème, générées par scripts/prepare_assets.py) ---
ASSET_BACKGROUND = "background.png"
ASSET_MENU = "menu.png"
ASSET_START = "start_screen.png"
# Animation et musique d'accueil (produites par scripts/prepare_assets.py).
ASSET_START_VIDEO = "start_video"
ASSET_START_AUDIO = "start_audio.ogg"
START_VIDEO_FPS = 15
ASSET_MENU_FRAME = "menu_frame.png"
ASSET_TITLE = "title.png"
ASSET_SCORE_SCREEN = "score_screen.png"
ASSET_PADDLE_LEFT = "paddle_left.png"
ASSET_PADDLE_RIGHT = "paddle_right.png"
ASSET_BALL = "ball.png"
# Police du thème, embarquée (licence OFL dans assets/OFL-Orbitron.txt).
ASSET_FONT = "Orbitron.ttf"
