"""Scène de jeu : déroule une partie (1 joueur contre l'IA, ou 2 joueurs)."""

import random

import pygame

from .. import settings
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

        left_x = settings.PADDLE_MARGIN
        right_x = settings.WINDOW_WIDTH - settings.PADDLE_MARGIN - settings.PADDLE_WIDTH
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
        # Petit délai avant chaque remise en jeu.
        if self.serve_timer > 0:
            self.serve_timer -= dt
            return

        keys = pygame.key.get_pressed()
        self._move_players(keys, dt)
        if self.ai is not None:
            self.ai.update(self.ball.y, self.right_paddle, dt)

        self.ball.update(dt)
        if self.ball.handle_walls():
            self.app.sound.wall_bounce()
        self._handle_paddles()
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
        ball = self.ball
        if ball.vx < 0 and ball.rect.colliderect(self.left_paddle.rect):
            ball.x = self.left_paddle.rect.right + ball.radius
            ball.bounce_off_paddle(self.left_paddle.center_y, direction=1)
            self._after_paddle_hit()
        elif ball.vx > 0 and ball.rect.colliderect(self.right_paddle.rect):
            ball.x = self.right_paddle.rect.left - ball.radius
            ball.bounce_off_paddle(self.right_paddle.center_y, direction=-1)
            self._after_paddle_hit()

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
        surface.fill(settings.BLACK)
        self._draw_net(surface)
        self._draw_scores(surface)
        pygame.draw.rect(surface, settings.WHITE, self.left_paddle.rect)
        pygame.draw.rect(surface, settings.WHITE, self.right_paddle.rect)
        pygame.draw.circle(surface, settings.ACCENT,
                           (int(self.ball.x), int(self.ball.y)), self.ball.radius)
        if self.serve_timer > 0:
            self.app.draw_text(surface, "Prêt !", self.app.font_medium, settings.GRAY,
                               center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2))
        self._draw_mode_label(surface)

    def _draw_scores(self, surface):
        center_x = settings.WINDOW_WIDTH // 2
        self.app.draw_text(surface, str(self.score.left), self.app.font_large,
                           settings.WHITE, center=(center_x - 80, 60))
        self.app.draw_text(surface, str(self.score.right), self.app.font_large,
                           settings.WHITE, center=(center_x + 80, 60))

    @staticmethod
    def _draw_net(surface):
        for y in range(0, settings.WINDOW_HEIGHT, 30):
            pygame.draw.rect(surface, settings.DARK_GRAY,
                             (settings.WINDOW_WIDTH // 2 - 2, y, 4, 16))

    def _draw_mode_label(self, surface):
        if self.mode == "1p":
            label = f"1 joueur — {self.level}"
        else:
            label = "2 joueurs"
        self.app.draw_text(surface, label, self.app.font_small, settings.GRAY,
                           topleft=(10, 10))
