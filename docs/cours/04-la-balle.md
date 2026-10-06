# 04 — La balle

## Objectifs

À la fin de ce chapitre, vous saurez :

- représenter un déplacement par un **vecteur vitesse** ;
- faire rebondir une balle sur les bords **haut et bas** sans qu'elle se « colle » ;
- détecter qu'une balle est **sortie** du terrain ;
- renvoyer la balle avec un **angle qui dépend du point d'impact** (la « physique
  Pong ») ;
- accélérer progressivement le jeu à chaque échange.

**Fichiers du projet :** `pong/ball.py`, `pong/scenes/game.py`, `pong/settings.py`
**Test du projet :** `tests/test_ball.py`

## 1. Un déplacement, c'est deux nombres

Jusqu'ici, la raquette ne bougeait que verticalement. La balle, elle, va dans
**toutes les directions**. On la décrit par :

- sa **position** : `x`, `y` ;
- sa **vitesse** : `vx` (horizontale) et `vy` (verticale), en pixels par seconde.

C'est un **vecteur vitesse** :

```
        vy > 0  (descend)
          │
          ●─── vx > 0 (va à droite)
        ╱
```

À chaque image, on ajoute simplement la vitesse multipliée par le temps écoulé :

```python
self.x += self.vx * dt
self.y += self.vy * dt
```

## 2. Lancer la balle dans une direction

Ajoutez à `settings.py` :

```python
# --- Balle ---
BALL_RADIUS = 8
BALL_START_SPEED = 360      # pixels par seconde
BALL_SPEEDUP = 22           # gain de vitesse à chaque échange
BALL_MAX_SPEED = 820
MAX_BOUNCE_ANGLE = 60       # angle maximal de rebond, en degrés
```

Puis la classe `Ball`. La mise en jeu choisit une direction **au hasard**, dans un
cône de 60° :

```python
    def reset(self, direction=None):
        self.x = (settings.FIELD_LEFT + settings.FIELD_RIGHT) / 2
        self.y = (settings.FIELD_TOP + settings.FIELD_BOTTOM) / 2
        self.speed = settings.BALL_START_SPEED
        if direction is None:
            direction = random.choice((-1, 1))
        angle = math.radians(random.uniform(-30, 30))
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)
```

### Un peu de trigonométrie

On veut une **vitesse totale constante** (`speed`) mais une **direction variable**.
Si `θ` est l'angle par rapport à l'horizontale, alors :

| Composante | Formule |
|------------|---------|
| horizontale | `vx = speed × cos(θ)` |
| verticale | `vy = speed × sin(θ)` |

```
                 ●  vx = speed·cos θ
                ╱│  vy = speed·sin θ
              ╱  │  (vx² + vy² = speed²)
            ╱____│
              θ
```

- `math.radians(30)` convertit 30 degrés en radians (ce que Python attend).
- Entre **-30° et +30°**, la balle part franchement vers la gauche ou la droite,
  tout en variant légèrement.
- Le paramètre `direction` (+1/-1) permet de renvoyer la balle vers le joueur qui
  vient de marquer.

## 3. Rebondir sur les bords haut et bas

```python
    def handle_walls(self):
        """Rebondit sur les bords haut/bas. Renvoie True si un rebond a eu lieu."""
        if self.vy < 0 and self.y - self.radius <= settings.FIELD_TOP:
            self.y = settings.FIELD_TOP + self.radius
            self.vy = -self.vy
            return True
        if self.vy > 0 and self.y + self.radius >= settings.FIELD_BOTTOM:
            self.y = settings.FIELD_BOTTOM - self.radius
            self.vy = -self.vy
            return True
        return False
```

Trois points importants :

1. On teste `self.vy < 0` (la balle **monte**) avant de rebondir en haut. Sans ce
   test, une balle immobile posée sur le bord (`vy == 0`) verrait sa vitesse
   inversée à chaque image et **vibrerait** sur place.
2. On **replace** la balle à l'intérieur (`self.y = FIELD_TOP + self.radius`) avant
   d'inverser la vitesse. Sinon, une balle légèrement engagée dans le mur le
   retraverserait à l'image suivante et pourrait « sortir ».
3. On **renvoie `True`** : la scène saura qu'il faut jouer un son (chapitre 09).

## 4. Détecter la sortie

```python
    def off_screen(self):
        """Renvoie "left" ou "right" si la balle est sortie, sinon None."""
        if self.x + self.radius < settings.FIELD_LEFT:
            return "left"
        if self.x - self.radius > settings.FIELD_RIGHT:
            return "right"
        return None
```

On ne renvoie pas un booléen mais **le côté** : la scène en déduira quel joueur
marque le point.

## 5. Le rebond sur la raquette : la « physique Pong »

Un Pong amusant ne renvoie pas la balle toujours au même angle : **l'angle dépend
de l'endroit où on frappe**. Frapper avec le bord de la raquette envoie la balle
beaucoup plus en biais.

```
   ┌──┐ ← bord haut    → balle repart vers le haut
   │▐▐│
   │▐▐│ ← centre       → balle repart à plat
   │▐▐│
   └──┘ ← bord bas     → balle repart vers le bas
```

```python
    def bounce_off_paddle(self, paddle_center_y, direction):
        half = settings.PADDLE_HEIGHT / 2
        # offset dans [-1, 1] : -1 = bord haut, 0 = centre, +1 = bord bas
        offset = (self.y - paddle_center_y) / half
        offset = max(-1.0, min(1.0, offset))

        angle = math.radians(settings.MAX_BOUNCE_ANGLE * offset)
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

        # La balle accélère à chaque échange, jusqu'à un maximum.
        self.speed = min(self.speed + settings.BALL_SPEEDUP, settings.BALL_MAX_SPEED)
```

- `offset` vaut `-1` si la balle frappe le bord **haut**, `+1` le bord **bas**, `0`
  le centre.
- L'angle de sortie est proportionnel : `-60°`, `0°`, `+60°`.
- On **borne** `offset` : si la balle touche un tout petit peu au-delà du bord, on
  reste dans l'intervalle.
- La vitesse **augmente** à chaque échange : les parties ne s'éternisent pas.

> 💡 `direction` vaut `+1` quand la balle repart vers la **droite**, `-1` vers la
> **gauche**. C'est la scène qui le sait, car c'est elle qui vient de détecter la
> collision (chapitre 05).

## À vous de jouer !

1. Écrivez la classe `Ball` (`pong/ball.py`) avec `reset`, `update`,
   `handle_walls`, `bounce_off_paddle` et `off_screen`.
2. Écrivez les tests :
   - une balle qui monte rebondit sur le bord haut **et repart vers le bas** ;
   - une balle qui descend rebondit sur le bord bas ;
   - une balle immobile **ne bouge pas** (le bug du « tremblement ») ;
   - la balle qui sort à gauche est détectée (`"left"`) ;
   - frappée en haut de la raquette, la balle repart **vers le haut** ; au centre,
     **à plat**.
3. Branchez la balle dans `GameScene` : déplacez-la, faites-la rebondir, et
   **relancez-la au centre** dès qu'elle sort (pour l'instant, le point ne compte
   pas — ce sera le chapitre 07).

<details>
<summary>Un indice pour le rebond « qui repart vers le haut »</summary>

Après un rebond sur le **bord haut**, `vy` doit être **positif** (la balle descend).
Pour la raquette : frappée au-dessus du centre (`offset < 0`), l'angle est négatif,
donc `sin(angle) < 0` → `vy < 0` → la balle repart vers le haut. ✅

</details>

## Corrigé

### `pong/ball.py`

```python
"""La balle : déplacement, rebonds et accélération progressive.

La logique de ce module est pure (hors `pygame.Rect`), donc testable sans fenêtre.
Les positions sont exprimées en pixels, les vitesses en pixels par seconde.
"""

import math
import random

import pygame

from . import settings


class Ball:
    """Une balle de Pong."""

    def __init__(self, x=None, y=None, speed=settings.BALL_START_SPEED):
        self.x = (settings.FIELD_LEFT + settings.FIELD_RIGHT) / 2 if x is None else float(x)
        self.y = (settings.FIELD_TOP + settings.FIELD_BOTTOM) / 2 if y is None else float(y)
        self.radius = settings.BALL_RADIUS
        self.speed = float(speed)
        self.vx = 0.0
        self.vy = 0.0

    @property
    def rect(self):
        """Rectangle de collision (coin haut-gauche + dimensions)."""
        size = self.radius * 2
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), size, size)

    def reset(self, direction=None):
        """Replace la balle au centre et la relance.

        `direction` : +1 vers la droite, -1 vers la gauche (aléatoire si None).
        """
        self.x = (settings.FIELD_LEFT + settings.FIELD_RIGHT) / 2
        self.y = (settings.FIELD_TOP + settings.FIELD_BOTTOM) / 2
        self.speed = settings.BALL_START_SPEED
        if direction is None:
            direction = random.choice((-1, 1))
        angle = math.radians(random.uniform(-30, 30))
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

    def update(self, dt):
        """Avance la balle de `dt` secondes."""
        self.x += self.vx * dt
        self.y += self.vy * dt

    def handle_walls(self):
        """Rebondit sur les bords haut/bas. Renvoie True si un rebond a eu lieu.

        On ne corrige que si la balle se dirige *vers* le mur : évite de « coller »
        une balle immobile (vy == 0) et les doubles rebonds.
        """
        if self.vy < 0 and self.y - self.radius <= settings.FIELD_TOP:
            self.y = settings.FIELD_TOP + self.radius
            self.vy = -self.vy
            return True
        if self.vy > 0 and self.y + self.radius >= settings.FIELD_BOTTOM:
            self.y = settings.FIELD_BOTTOM - self.radius
            self.vy = -self.vy
            return True
        return False

    def bounce_off_paddle(self, paddle_center_y, direction):
        """Rebondit sur une raquette.

        L'angle de sortie dépend de l'écart entre le point d'impact et le centre
        de la raquette : plus la balle frappe près d'un bord, plus l'angle est
        prononcé (borné à MAX_BOUNCE_ANGLE).

        `direction` : +1 pour renvoyer vers la droite, -1 vers la gauche.
        """
        half = settings.PADDLE_HEIGHT / 2
        offset = (self.y - paddle_center_y) / half
        offset = max(-1.0, min(1.0, offset))

        angle = math.radians(settings.MAX_BOUNCE_ANGLE * offset)
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

        self.speed = min(self.speed + settings.BALL_SPEEDUP, settings.BALL_MAX_SPEED)

    def off_screen(self):
        """Renvoie "left" ou "right" si la balle est sortie, sinon None."""
        if self.x + self.radius < settings.FIELD_LEFT:
            return "left"
        if self.x - self.radius > settings.FIELD_RIGHT:
            return "right"
        return None
```

### `tests/test_ball.py` (extraits)

```python
"""Tests de la physique de la balle (sans fenêtre graphique)."""

import pytest

from pong import settings
from pong.ball import Ball


# --- Rebond sur les murs haut / bas ---

def test_bounce_off_top_wall():
    ball = Ball()
    ball.y = settings.FIELD_TOP + settings.BALL_RADIUS - 1
    ball.vy = -200.0
    bounced = ball.handle_walls()
    assert bounced is True
    assert ball.vy > 0
    assert ball.y == pytest.approx(settings.FIELD_TOP + settings.BALL_RADIUS)


def test_no_bounce_when_vy_is_zero():
    ball = Ball()
    ball.y = settings.FIELD_TOP + settings.BALL_RADIUS - 1
    ball.vy = 0.0
    assert ball.handle_walls() is False


# --- Rebond sur une raquette (angle selon le point d'impact) ---

def test_hit_paddle_top_sends_ball_upward():
    ball = Ball()
    center = 300.0
    ball.y = center - settings.PADDLE_HEIGHT / 2
    ball.bounce_off_paddle(paddle_center_y=center, direction=1)
    assert ball.vy < 0
    assert ball.vx > 0


# --- Sortie de terrain ---

def test_off_screen_left_and_right():
    ball = Ball()
    ball.x = settings.FIELD_LEFT - ball.radius - 1
    assert ball.off_screen() == "left"
    ball.x = settings.FIELD_RIGHT + ball.radius + 1
    assert ball.off_screen() == "right"
    ball.x = (settings.FIELD_LEFT + settings.FIELD_RIGHT) / 2
    assert ball.off_screen() is None
```

### Brancher la balle dans `GameScene`

```python
from ..ball import Ball
...

    def __init__(self, app, mode="1p"):
        ...
        self.ball = Ball()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self._move_players(keys, dt)

        self.ball.update(dt)
        self.ball.handle_walls()
        if self.ball.off_screen():
            # Les points viendront au chapitre 07 ; pour l'instant on relance.
            self.ball.reset()

    def _move_players(self, keys, dt):
        """Déplace chaque raquette selon les touches appuyées."""
        if any(keys[key] for key in settings.P1_UP):
            self.left_paddle.move_up(dt)
        if any(keys[key] for key in settings.P1_DOWN):
            self.left_paddle.move_down(dt)
        if self.mode == "2p":
            if any(keys[key] for key in settings.P2_UP):
                self.right_paddle.move_up(dt)
            if any(keys[key] for key in settings.P2_DOWN):
                self.right_paddle.move_down(dt)

    def draw(self, surface):
        surface.fill(BACKGROUND_COLOR)
        pygame.draw.rect(surface, settings.NEON_CYAN, self.left_paddle.rect)
        pygame.draw.rect(surface, settings.NEON_PINK, self.right_paddle.rect)
        pygame.draw.circle(surface, settings.NEON_YELLOW,
                           (self.ball.x, self.ball.y), self.ball.radius)
```

N'oubliez pas la couleur dans `settings.py` :

```python
NEON_YELLOW = (255, 214, 102)
```

La balle rebondit maintenant en haut et en bas, et sort par les côtés. **Il ne
manque que les raquettes !** Ce sera l'objet du prochain chapitre.

> **Dans le projet de référence :** `pong/ball.py` correspond exactement à ce
> corrigé. Seul `BALL_RADIUS` (8) et la taille du sprite de balle
> (`2 × BALL_RADIUS`) seront alignés au chapitre 11.

## En résumé

- La vitesse est un **vecteur** `(vx, vy)` ; on avance de `v × dt`.
- Un lancer utilise la **trigonométrie** : `vx = speed·cos θ`, `vy = speed·sin θ`.
- Un rebond teste la **direction** (`vy < 0`) pour éviter les vibrations.
- On **replace** la balle dans le terrain avant d'inverser la vitesse.
- L'angle de renvoi dépend du **point d'impact** sur la raquette — c'est ce qui
  rend le jeu intéressant.

## Étape suivante

→ [05 — Les collisions](05-les-collisions.md)
