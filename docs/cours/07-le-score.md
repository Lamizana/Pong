# 07 — Le score et la victoire

## Objectifs

À la fin de ce chapitre, vous saurez :

- modéliser les **règles** du jeu dans une classe toute simple ;
- détecter qu'un point est marqué et **à qui** il revient ;
- gérer la **remise en jeu** (délai, direction, repositionnement) ;
- **afficher** le score à l'écran ;
- arrêter la partie quand un joueur atteint le nombre de points requis.

**Fichiers du projet :** `pong/score.py`, `pong/scenes/game.py`, `pong/settings.py`
**Test du projet :** `tests/test_score.py`

## 1. Les règles en une phrase

> Un point est marqué quand la balle sort **derrière** une raquette.
> Le premier à **5 points** gagne.

Encore une fois, ce sont des **règles** : aucune image, aucune fenêtre. On les met
dans leur propre module, et on les teste.

Ajoutez à `settings.py` :

```python
# --- Score ---
POINTS_TO_WIN = 5
```

## 2. La classe `Score`

```python
class Score:
    def __init__(self, points_to_win=POINTS_TO_WIN):
        self.points_to_win = points_to_win
        self.reset()

    def reset(self):
        self.left = 0
        self.right = 0

    def add_point(self, side):
        if side == "left":
            self.left += 1
        elif side == "right":
            self.right += 1
        else:
            raise ValueError(f"côté invalide : {side!r} (attendu 'left' ou 'right')")
        return self.winner()

    def winner(self):
        if self.left >= self.points_to_win:
            return "left"
        if self.right >= self.points_to_win:
            return "right"
        return None
```

Remarquez la **valeur renvoyée** par `add_point` : le vainqueur, ou `None`. L'appelant
n'a donc pas besoin de demander séparément « est-ce fini ? » puis « qui a gagné ? » —
une seule opération, une seule réponse.

Le paramètre `points_to_win` rend la règle **configurable** : les options du menu la
régleront sur 3, 5 ou 10 (chapitre 08). C'est aussi ce qui rend le test de victoire
plus rapide à écrire : `Score(points_to_win=1)`.

## 3. Compter les points dans la scène

La balle sort d'un côté, c'est le camp **opposé** qui marque :

```python
side = self.ball.off_screen()
if side is None:
    return

# Balle sortie à gauche => le camp droit marque, et inversement.
scorer = "right" if side == "left" else "left"
winner = self.score.add_point(scorer)
```

## 4. La remise en jeu

Un point marqué, et la balle téléportée au centre instantanément ? Brutal. On
instaure une courte pause — un **décompte** — pendant lequel le joueur peut se
repositionner :

```
        ●  « Prêt ! »          → 1 seconde plus tard, la balle part
```

```python
        # Remise en jeu vers le camp qui vient d'encaisser le point.
        self.serve_direction = 1 if scorer == "left" else -1
        self.serve_timer = 1.0
        self.ball.reset(direction=self.serve_direction)
        self.left_paddle.reset()
        self.right_paddle.reset()
```

- `serve_direction` : la balle part vers celui qui vient d'encaisser — équitable.
- `serve_timer` : un compte à rebours en secondes. Tant qu'il est positif, la balle
  **ne bouge pas** (mais les raquettes restent contrôlables).
- On **recentre** les raquettes, sinon un joueur mal placé serait pénalisé deux fois.

Dans `update` :

```python
        if self.serve_timer > 0:
            self.serve_timer -= dt
            return                       # la balle attend encore
```

## 5. Afficher le score

Il faut pouvoir lire le score. Au chapitre 02, nous n'avions pas encore de texte.
Ajoutons un petit utilitaire à `App` :

```python
    def draw_text(self, surface, text, font, color, center=None, topleft=None):
        """Petit utilitaire de rendu de texte, renvoie le rectangle occupé."""
        image = font.render(text, True, color)
        rect = image.get_rect()
        if center is not None:
            rect.center = center
        if topleft is not None:
            rect.topleft = topleft
        surface.blit(image, rect)
        return rect
```

Et les polices dans `App.__init__` :

```python
        self.font_small = pygame.font.SysFont(None, 28)
        self.font_medium = pygame.font.SysFont(None, 44)
        self.font_large = pygame.font.SysFont(None, 72)
```

> 💡 `SysFont(None, taille)` utilise la police système par défaut : aucune ressource
> à embarquer. Au chapitre 12, nous la remplacerons par une **vraie police** venue
> d'un fichier — sans changer une seule ligne des scènes, puisque tout passe par
> `draw_text`.

Puis, dans la scène :

```python
    def _draw_scores(self, surface):
        center_x = settings.WINDOW_WIDTH // 2
        y = settings.FIELD_TOP - 40
        self.app.draw_text(surface, str(self.score.left), self.app.font_medium,
                           settings.NEON_CYAN, center=(center_x - 60, y))
        self.app.draw_text(surface, str(self.score.right), self.app.font_medium,
                           settings.NEON_PINK, center=(center_x + 60, y))
```

> **Dans le projet de référence :** ces chiffres seront posés dans un **panneau de
> score** issu du décor (chapitre 11), et la victoire ouvrira l'écran de fin
> (chapitre 10). Pour l'instant, contentons-nous d'un affichage lisible.

## À vous de jouer !

1. Écrivez la classe `Score` (`pong/score.py`).
2. Écrivez les tests :
   - un score neuf vaut 0 – 0 ;
   - marquer à gauche incrémente **seulement** la gauche ;
   - un côté invalide lève `ValueError` ;
   - `Score(points_to_win=2)` : le troisième point déclare un vainqueur, pas le
     deuxième ;
   - `reset()` remet tout à zéro.
3. Dans `GameScene`, comptez les points quand la balle sort, remettez en jeu avec
   le décompte, et affichez le score.
4. Quand quelqu'un gagne… contentez-vous d'afficher « Partie terminée » au centre
   pour le moment (le vrai écran de fin arrive au chapitre 10).

<details>
<summary>Un indice sur le décompte</summary>

N'oubliez pas de **décrémenter** `serve_timer` et de **sortir** de `update` par un
`return` tant qu'il est positif : la balle ne doit pas avancer, mais les raquettes,
si.

</details>

## Corrigé

### `pong/score.py`

```python
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
```

### `tests/test_score.py`

```python
"""Tests du score et de la condition de victoire."""

import pytest

from pong.score import Score


def test_new_score_is_zero_zero():
    score = Score()

    assert (score.left, score.right) == (0, 0)
    assert score.winner() is None


def test_add_point_only_counts_the_right_side():
    score = Score()

    score.add_point("left")

    assert score.left == 1
    assert score.right == 0


def test_invalid_side_is_rejected():
    with pytest.raises(ValueError):
        Score().add_point("milieu")


def test_winner_is_detected_at_the_configured_threshold():
    score = Score(points_to_win=2)

    assert score.add_point("left") is None     # 1 point
    assert score.add_point("left") == "left"   # 2 points : victoire


def test_reset_clears_both_sides():
    score = Score()
    score.add_point("left")
    score.add_point("right")

    score.reset()

    assert (score.left, score.right) == (0, 0)
```

### `GameScene` — le score et la remise en jeu

```python
from ..score import Score
...

    def __init__(self, app, mode="1p", level="moyen", points_to_win=settings.POINTS_TO_WIN):
        ...
        self.score = Score(points_to_win=points_to_win)
        self.serve_timer = 1.0
        self.serve_direction = random.choice((-1, 1))
        self.ball.reset(direction=self.serve_direction)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self._move_players(keys, dt)
        if self.ai is not None:
            self.ai.update(self.ball.y, self.right_paddle, dt)

        if self.serve_timer > 0:
            self.serve_timer -= dt
            return

        self._advance_ball(dt)
        self._handle_score()

    def _handle_score(self):
        side = self.ball.off_screen()
        if side is None:
            return

        scorer = "right" if side == "left" else "left"
        winner = self.score.add_point(scorer)
        if winner is not None:
            self.game_over = winner      # l'écran de fin arrive au chapitre 10
            return

        self.serve_direction = 1 if scorer == "left" else -1
        self.serve_timer = 1.0
        self.ball.reset(direction=self.serve_direction)
        self.left_paddle.reset()
        self.right_paddle.reset()
        if self.ai is not None:
            self.ai.randomize_offset()

    def draw(self, surface):
        surface.fill(BACKGROUND_COLOR)
        pygame.draw.rect(surface, settings.NEON_CYAN, self.left_paddle.rect)
        pygame.draw.rect(surface, settings.NEON_PINK, self.right_paddle.rect)
        pygame.draw.circle(surface, settings.NEON_YELLOW,
                           (self.ball.x, self.ball.y), self.ball.radius)
        self._draw_scores(surface)
        if self.serve_timer > 0:
            self.app.draw_text(surface, "Prêt !", self.app.font_medium,
                               settings.NEON_YELLOW,
                               center=(settings.WINDOW_WIDTH // 2,
                                       settings.WINDOW_HEIGHT // 2 + 80))
```

Vous avez maintenant **un Pong complet qui se joue** : deux raquettes, une balle,
une IA, un score et une victoire. La partie 2 est terminée ! 🏓

> **Dans le projet de référence :** `pong/score.py` est identique. La scène ajoutera
> le son, la pause et l'écran de fin aux chapitres suivants.

## En résumé

- Les **règles** (le score) vivent dans leur propre module, sans affichage : on les
  teste en trois lignes.
- `add_point` renvoie **directement** le vainqueur : une opération, une réponse.
- Une **remise en jeu** avec décompte et recentrage rend le jeu équitable.
- Un utilitaire `draw_text` centralise le rendu du texte — pratique pour tout
  afficher, et pour changer de police plus tard sans rien casser.

## Étape suivante

→ [08 — Le menu et les options](08-le-menu-et-les-options.md)
