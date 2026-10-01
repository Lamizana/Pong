"""Scène de jeu : déroule une partie (1 joueur contre l'IA, ou 2 joueurs)."""

import random

import pygame

from .. import settings, synthwave
from ..ai import AI
from ..ball import Ball
from ..paddle import Paddle
from ..score import Score
from .base import Scene
from .gameover import GameOverScene
from .pause import PauseScene


class GameScene(Scene):
    def __init__(self, app, mode="1p", level="moyen"):
        super().__init__(app)
        self.mode = mode
        self.level = level

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
        self.score = Score()
        self.ai = AI(level=level) if mode == "1p" else None

        self.serve_timer = 1.0
        self.serve_direction = random.choice((-1, 1))
        self.ball.reset(direction=self.serve_direction)

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
        ball = self.ball
        if ball.vx < 0 and ball.rect.colliderect(self.left_paddle.rect):
            ball.x = self.left_paddle.rect.right + ball.radius
            ball.bounce_off_paddle(self.left_paddle.center_y, direction=1)
            self._after_paddle_hit()
            return True
        if ball.vx > 0 and ball.rect.colliderect(self.right_paddle.rect):
            ball.x = self.right_paddle.rect.left - ball.radius
            ball.bounce_off_paddle(self.right_paddle.center_y, direction=-1)
            self._after_paddle_hit()
            return True
        return False

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
            self.app.set_scene(GameOverScene(self.app, winner, self.mode, self.level))
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
            synthwave.glow_text(surface, self.app.font_medium, "Prêt !",
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
        ball = self.app.assets.ball
        surface.blit(ball, (self.ball.x - ball.get_width() / 2,
                            self.ball.y - ball.get_height() / 2))

    def _draw_scores(self, surface):
        center_x = settings.WINDOW_WIDTH // 2
        synthwave.glow_text(surface, self.app.font_large, str(self.score.left),
                            settings.NEON_CYAN, center=(center_x - 80, 60))
        synthwave.glow_text(surface, self.app.font_large, str(self.score.right),
                            settings.NEON_PINK, center=(center_x + 80, 60))

    def _draw_mode_label(self, surface):
        if self.mode == "1p":
            label = settings.AI_LEVELS[self.level]["label"]
        else:
            label = "2 joueurs"
        self.app.draw_text(surface, label, self.app.font_small, settings.TEXT_DIM,
                           topleft=(10, 10))
