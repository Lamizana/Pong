# 06 — L'IA

## Objectifs

À la fin de ce chapitre, vous saurez :

- piloter une raquette **automatiquement** ;
- régler une difficulté par **deux paramètres** : la vitesse et l'imprécision ;
- rendre l'adversaire **battable** (et agréable à jouer) ;
- éviter le **tremblement** grâce à une zone morte ;
- tester un comportement aléatoire de façon **déterministe**.

**Fichiers du projet :** `pong/ai.py`, `pong/settings.py`
**Test du projet :** `tests/test_ai.py`

## 1. Le principe

En mode 1 joueur, la raquette de droite est contrôlée par l'ordinateur. L'idée la
plus simple : **elle suit la balle**.

```python
if ball.y < paddle.center_y:
    paddle.move_up(dt)
else:
    paddle.move_down(dt)
```

Cette IA-là est **imbattable** : elle ne rate jamais rien. Un adversaire parfait
n'est pas amusant — il faut lui donner deux faiblesses **contrôlées** :

1. une **vitesse limitée** : elle ne peut pas rattraper une balle trop rapide ;
2. une **imprécision de visée** : elle vise à côté, un peu au hasard.

## 2. Les niveaux de difficulté

Ajoutez à `settings.py` :

```python
# --- IA : réglages ---
AI_DEAD_ZONE = 6            # tolérance (px) autour de la cible, évite le tremblement

# --- IA : niveaux de difficulté ---
# speed : vitesse maximale de la raquette de l'IA (px/s)
# error : écart maximal (px) visé par rapport au centre de la balle
AI_LEVELS = {
    "facile":    {"speed": 300, "error": 70, "label": "Facile"},
    "moyen":     {"speed": 440, "error": 35, "label": "Moyen"},
    "difficile": {"speed": 640, "error": 8,  "label": "Difficile"},
}
```

Un **dictionnaire de dictionnaires** : chaque niveau rassemble ses réglages et son
libellé. C'est facile à lire, et ajouter un niveau « impossible » ne demande qu'une
ligne.

| Niveau | Vitesse | Imprécision | Ressenti |
|--------|---------|-------------|----------|
| Facile | 300 px/s | ±70 px | rate souvent, laisse passer |
| Moyen | 440 px/s | ±35 px | équilibré |
| Difficile | 640 px/s | ±8 px | très présent, mais pas parfait |

> 💡 La vitesse du joueur est `PADDLE_SPEED = 520`. En « facile », l'IA est donc
> **plus lente** que vous : vous pouvez la déborder.

## 3. La zone morte : éviter le tremblement

Si l'IA vise une cible et s'y arrête pile, elle oscille : elle monte, se retrouve
un pixel trop haut, redescend… Ce **tremblement** est laid et donne une impression
de panique.

La parade : ne rien faire tant qu'on est **assez proche** de la cible.

```python
if abs(diff) <= settings.AI_DEAD_ZONE:
    return
```

## 4. La classe `AI`

```python
class AI:
    def __init__(self, level="moyen", rng=None):
        if level not in settings.AI_LEVELS:
            raise ValueError(f"niveau inconnu : {level!r}")
        config = settings.AI_LEVELS[level]
        self.level = level
        self.speed = config["speed"]
        self.error = config["error"]
        self._rng = rng or random.Random()
        self.target_offset = 0.0
```

Deux détails de qualité :

- **Un niveau inconnu lève une erreur claire** plutôt que de planter plus loin
  avec un `KeyError` obscur. (« Échouer tôt, échouer fort. »)
- **Le générateur aléatoire est injectable** (`rng`). Les tests pourront lui passer
  un `random.Random(42)`, dont la suite de nombres est **toujours la même** : on
  teste un comportement aléatoire sans qu'il soit imprévisible.

## 5. Viser… à côté

L'imprécision n'est pas tirée à chaque image (l'IA tremblerait), mais **une fois
par échange** : quand elle touche la balle, elle choisit une nouvelle erreur de
visée.

```python
    def randomize_offset(self):
        """Tire une nouvelle imprécision de visée (à chaque nouvel échange)."""
        self.target_offset = self._rng.uniform(-self.error, self.error)
```

## 6. Se déplacer

```python
    def update(self, ball_y, paddle, dt):
        """Déplace `paddle` vers la balle, sans dépasser la vitesse du niveau."""
        target = ball_y + self.target_offset
        diff = target - paddle.center_y
        if abs(diff) <= settings.AI_DEAD_ZONE:
            return                      # assez proche : on ne bouge pas
        direction = 1 if diff > 0 else -1
        step = min(abs(diff), self.speed * dt)
        paddle.move_by(direction * step)
```

La ligne essentielle est `step = min(abs(diff), self.speed * dt)` :

- `self.speed * dt` est la distance **maximale** parcourable en `dt` secondes ;
- si la cible est plus proche que cela, on s'arrête **exactement** dessus
  (`abs(diff)`), sans la dépasser.

C'est ce qui évite de « dépasser puis revenir en arrière » — un autre tremblement.

Notez que l'IA utilise `paddle.move_by` (le déplacement **brut**) et non
`paddle.move` : elle calcule elle-même sa distance, et `move_by` continue de
respecter les bornes du terrain. C'est exactement pourquoi nous avions découpé les
deux méthodes au chapitre 03.

## À vous de jouer !

1. Ajoutez `AI_LEVELS` et `AI_DEAD_ZONE` à `settings.py`.
2. Écrivez la classe `AI` (`pong/ai.py`).
3. Écrivez les tests, avec un `rng` déterministe :
   - un niveau inconnu lève `ValueError` ;
   - l'IA **descend** quand la balle est sous elle ;
   - l'IA **monte** quand la balle est au-dessus ;
   - elle ne parcourt **jamais** plus que `speed × dt` en une image ;
   - dans la zone morte, elle **ne bouge pas** (anti-tremblement).
4. Branchez l'IA dans `GameScene` : en mode `"1p"`, elle pilote la raquette de
   droite ; en mode `"2p"`, c'est le clavier.

<details>
<summary>Un indice pour tester proprement</summary>

```python
import random
from pong.ai import AI
from pong.paddle import Paddle

ai = AI(level="moyen", rng=random.Random(1))
ai.randomize_offset()

# ou, pour neutraliser l'imprécision dans un test de déplacement :
ai.target_offset = 0.0
```

</details>

## Corrigé

### `pong/ai.py`

```python
"""L'IA : pilote une raquette pour affronter le joueur en mode 1 joueur.

La difficulté règle deux paramètres : la vitesse maximale de la raquette et
l'imprécision de la visée (`error`). Une visée décalée rend l'IA battable même
lorsqu'elle pourrait suivre parfaitement la balle.

Logique pure : testable sans fenêtre ni boucle de jeu.
"""

import random

from . import settings


class AI:
    """Un adversaire automatique contrôlant une raquette."""

    def __init__(self, level="moyen", rng=None):
        if level not in settings.AI_LEVELS:
            raise ValueError(f"niveau inconnu : {level!r}")
        config = settings.AI_LEVELS[level]
        self.level = level
        self.speed = config["speed"]
        self.error = config["error"]
        self._rng = rng or random.Random()
        self.target_offset = 0.0

    def randomize_offset(self):
        """Tire une nouvelle imprécision de visée (à chaque nouvel échange)."""
        self.target_offset = self._rng.uniform(-self.error, self.error)

    def update(self, ball_y, paddle, dt):
        """Déplace `paddle` vers la balle, sans dépasser la vitesse du niveau."""
        target = ball_y + self.target_offset
        diff = target - paddle.center_y
        if abs(diff) <= settings.AI_DEAD_ZONE:
            return  # assez proche : on ne bouge pas (évite le tremblement)
        direction = 1 if diff > 0 else -1
        step = min(abs(diff), self.speed * dt)
        paddle.move_by(direction * step)
```

### `tests/test_ai.py` (extraits)

```python
"""Tests de l'IA : niveaux, déplacement borné et zone morte."""

import random

import pytest

from pong import settings
from pong.ai import AI
from pong.paddle import Paddle


def _paddle():
    return Paddle(settings.FIELD_RIGHT - settings.PADDLE_INSET)


def test_unknown_level_is_rejected():
    with pytest.raises(ValueError):
        AI(level="impossible")


def test_ai_moves_towards_the_ball():
    ai = AI(level="moyen", rng=random.Random(1))
    ai.target_offset = 0.0
    paddle = _paddle()
    paddle.y = settings.FIELD_TOP

    ai.update(ball_y=paddle.y + 200, paddle=paddle, dt=0.05)

    assert paddle.y > settings.FIELD_TOP          # elle est descendue


def test_ai_never_exceeds_its_speed():
    ai = AI(level="moyen", rng=random.Random(1))
    ai.target_offset = 0.0
    paddle = _paddle()
    paddle.y = settings.FIELD_TOP

    ai.update(ball_y=settings.FIELD_BOTTOM, paddle=paddle, dt=0.01)

    assert paddle.y - settings.FIELD_TOP <= ai.speed * 0.01 + 1e-9


def test_ai_does_not_jitter_inside_the_dead_zone():
    ai = AI(level="difficile", rng=random.Random(1))
    ai.target_offset = 0.0
    paddle = _paddle()

    ai.update(ball_y=paddle.center_y + 1, paddle=paddle, dt=0.05)

    assert paddle.y == settings.FIELD_TOP + (settings.FIELD_HEIGHT - paddle.height) / 2
```

### Le branchement dans `GameScene`

```python
from ..ai import AI
from ..ball import Ball
from ..paddle import Paddle
from ..score import Score
...

    def __init__(self, app, mode="1p", level="moyen"):
        super().__init__(app)
        self.mode = mode
        self.left_paddle = Paddle(settings.FIELD_LEFT + settings.PADDLE_INSET)
        self.right_paddle = Paddle(
            settings.FIELD_RIGHT - settings.PADDLE_INSET - settings.PADDLE_WIDTH)
        self.ball = Ball()
        self.score = Score()
        self.ai = AI(level=level) if mode == "1p" else None

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self._move_players(keys, dt)
        if self.ai is not None:
            self.ai.update(self.ball.y, self.right_paddle, dt)
        ...
```

Vous pouvez maintenant jouer **seul contre l'IA** : au menu, lancez le mode
`"1p"` avec `level="facile"`, puis `"difficile"`. La différence se sent
immédiatement.

> **Dans le projet de référence :** `pong/ai.py` est identique. Le `level` ne sera
> plus passé par le menu mais lu dans les **options** (chapitre 08), et l'IA
> recevra une nouvelle visée après chaque échange (`randomize_offset` appelé par la
> scène).

## En résumé

- Une IA parfaite n'est pas amusante : on la rend **battable** (vitesse + erreur).
- Une **zone morte** et un déplacement borné (`min(abs(diff), speed*dt)`) évitent
  les tremblements.
- Un **générateur aléatoire injectable** rend un comportement aléatoire testable.
- Valider les entrées (`ValueError` sur un niveau inconnu) échoue **tôt** et
  clairement.

## Étape suivante

→ [07 — Le score et la victoire](07-le-score.md)
