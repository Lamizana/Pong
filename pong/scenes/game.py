"""Scène de jeu : déroule une partie (1 joueur contre l'IA, ou 2 joueurs)."""

import math
import random

import pygame

from .. import neon, settings
from ..ai import AI
from ..ball import Ball
from ..collision import circle_rect_contact
from ..paddle import Paddle
from ..score import Score
from .base import Scene
from .gameover import GameOverScene
from .pause import PauseScene


class GameScene(Scene):
    def __init__(self, app, mode="1p"):
        super().__init__(app)
        self.mode = mode
        # Difficulté et points pour gagner viennent des options (app.config).
        self.level = app.config["level"]
        self.points_to_win = app.config["points_to_win"]

        # Raquettes placées à l'intérieur du cadre bleu néon : le sprite s'étend
        # vers le bord du terrain, sa zone de frappe restant sur le bord intérieur.
        left_sprite = app.assets.paddle_left.get_width()
        right_sprite = app.assets.paddle_right.get_width()
        left_x = (settings.FIELD_LEFT + settings.PADDLE_INSET
                  + left_sprite - settings.PADDLE_WIDTH)
        right_x = settings.FIELD_RIGHT - settings.PADDLE_INSET - right_sprite
        self.left_paddle = Paddle(x=left_x)
        self.right_paddle = Paddle(x=right_x)
        self.ball = Ball()
        self.score = Score(points_to_win=self.points_to_win)
        self.ai = AI(level=self.level) if mode == "1p" else None

        self.serve_timer = 1.0
        self.serve_direction = random.choice((-1, 1))
        self.ball.reset(direction=self.serve_direction)
        self.ball_angle = 0.0   # rotation visuelle de la balle (degrés)

    # --- Événements ---

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in settings.KEY_PAUSE:
            self.app.set_scene(PauseScene(self.app, self))

    # --- Mise à jour ---

    def update(self, dt):
        # Les raquettes restent contrôlables pendant le décompte de remise en jeu :
        # les joueurs peuvent se repositionner avant le service.
        keys = pygame.key.get_pressed()
        self._move_players(keys, dt)
        if self.ai is not None:
            self.ai.update(self.ball.y, self.right_paddle, dt)

        if self.serve_timer > 0:
            self.serve_timer -= dt
            return

        self._advance_ball(dt)
        self._spin_ball(dt)

    def _spin_ball(self, dt):
        """Fait rouler la balle sur elle-même, proportionnellement à sa vitesse."""
        spin = math.degrees(self.ball.vx / max(1.0, self.ball.radius))
        self.ball_angle = (self.ball_angle + spin * dt * settings.BALL_SPIN_FACTOR) % 360

    def _advance_ball(self, dt):
        # On découpe le pas de temps : la balle ne doit jamais avancer de plus que
        # son rayon en une sous-étape, sinon elle pourrait traverser une raquette
        # sans collision (« tunneling ») lors d'une image lente ou d'une balle rapide.
        distance = max(abs(self.ball.vx), abs(self.ball.vy)) * dt
        steps = max(1, int(distance / self.ball.radius) + 1)
        sub_dt = dt / steps

        for _ in range(steps):
            self.ball.update(sub_dt)
            if self.ball.handle_walls():
                self.app.sound.wall_bounce()
            if self._handle_paddles():
                break
            if self.ball.off_screen() is not None:
                break

        self._handle_score()

    def _move_players(self, keys, dt):
        if any(keys[key] for key in settings.P1_UP):
            self.left_paddle.move_up(dt)
        if any(keys[key] for key in settings.P1_DOWN):
            self.left_paddle.move_down(dt)
        if self.mode == "2p":
            if any(keys[key] for key in settings.P2_UP):
                self.right_paddle.move_up(dt)
            if any(keys[key] for key in settings.P2_DOWN):
                self.right_paddle.move_down(dt)

    def _handle_paddles(self):
        """Gère l'éventuelle collision balle/raquette. Renvoie True si une a eu lieu."""
        if self._resolve_paddle(self.left_paddle, direction=1):
            self._after_paddle_hit()
            return True
        if self._resolve_paddle(self.right_paddle, direction=-1):
            self._after_paddle_hit()
            return True
        return False

    def _resolve_paddle(self, paddle, direction):
        """Détecte et résout une collision balle/raquette (cercle vs rectangle).

        `direction` : +1 renvoie la balle vers la droite (raquette gauche), -1
        vers la gauche. La détection par cercle (et non par boîte englobante)
        évite que la balle traverse la raquette sur un coin. Renvoie True si une
        collision a été traitée.
        """
        ball = self.ball
        # Ne tester que si la balle se dirige vers cette raquette.
        if ball.vx * direction >= 0:
            return False

        rect = paddle.rect
        contact = circle_rect_contact(ball.x, ball.y, ball.radius, rect)
        if contact is None:
            return False

        (normal_x, normal_y), penetration = contact
        if rect.top <= ball.y <= rect.bottom:
            # Face latérale : rebond horizontal, angle selon le point d'impact.
            ball.x = rect.right + ball.radius if direction > 0 else rect.left - ball.radius
        else:
            # Coin haut/bas : on ressort la balle le long de la normale.
            ball.x += normal_x * penetration
            ball.y += normal_y * penetration
        ball.bounce_off_paddle(paddle.center_y, direction=direction)
        return True

    def _after_paddle_hit(self):
        self.app.sound.paddle_hit()
        if self.ai is not None:
            self.ai.randomize_offset()  # nouvelle visée pour le prochain échange

    def _handle_score(self):
        side = self.ball.off_screen()
        if side is None:
            return

        # Balle sortie à gauche => le camp droit marque, et inversement.
        scorer = "right" if side == "left" else "left"
        winner = self.score.add_point(scorer)
        self.app.sound.point_scored()

        if winner is not None:
            self.app.sound.win()
            self.app.set_scene(GameOverScene(self.app, winner, self.mode))
            return

        # Remise en jeu vers le camp qui vient d'encaisser le point.
        self.serve_direction = 1 if scorer == "left" else -1
        self.serve_timer = 1.0
        self.ball.reset(direction=self.serve_direction)
        self.left_paddle.reset()
        self.right_paddle.reset()
        if self.ai is not None:
            self.ai.randomize_offset()

    # --- Affichage ---

    def draw(self, surface):
        surface.blit(self.app.assets.background, (0, 0))
        self._draw_paddles(surface)
        self._draw_ball(surface)
        self._draw_scores(surface)

        if self.serve_timer > 0:
            neon.glow_text(surface, self.app.font_medium, "Prêt !",
                                settings.NEON_YELLOW,
                                center=(settings.WINDOW_WIDTH // 2,
                                        settings.WINDOW_HEIGHT // 2 + 80))
        self._draw_mode_label(surface)

    def _draw_paddles(self, surface):
        """Blitte les sprites, zone de frappe alignée sur le bord intérieur."""
        left = self.app.assets.paddle_left
        right = self.app.assets.paddle_right
        surface.blit(left, (self.left_paddle.rect.right - left.get_width(),
                            self.left_paddle.center_y - left.get_height() // 2))
        surface.blit(right, (self.right_paddle.rect.left,
                             self.right_paddle.center_y - right.get_height() // 2))

    def _draw_ball(self, surface):
        sprite = self.app.assets.ball
        if self.ball_angle:
            sprite = pygame.transform.rotate(sprite, self.ball_angle)
        surface.blit(sprite, (self.ball.x - sprite.get_width() / 2,
                              self.ball.y - sprite.get_height() / 2))

    def _draw_scores(self, surface):
        # Panneau de score, posé au-dessus du terrain (dans le ciel).
        center_x = settings.WINDOW_WIDTH // 2
        screen = self.app.assets.score_screen
        rect = screen.get_rect(midtop=(center_x, 2))
        surface.blit(screen, rect)

        # Le score, à l'intérieur du panneau (texte sombre, lisible sur cyan).
        y = rect.centery
        color = (4, 32, 46)
        self.app.draw_text(surface, str(self.score.left), self.app.font_small,
                           color, center=(center_x - 27, y))
        self.app.draw_text(surface, str(self.score.right), self.app.font_small,
                           color, center=(center_x + 27, y))

    def _draw_mode_label(self, surface):
        if self.mode == "1p":
            label = "1 joueur — " + settings.AI_LEVELS[self.level]["label"]
        else:
            label = "2 joueurs"
        self.app.draw_text(surface, label, self.app.font_small, settings.TEXT_DIM,
                           topleft=(10, 10))
