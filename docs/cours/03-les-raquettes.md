# 03 — Les raquettes

## Objectifs

À la fin de ce chapitre, vous saurez :

- modéliser une **entité** du jeu par une classe (données + méthodes) ;
- utiliser `pygame.Rect`, l'outil fourre-tout de pygame ;
- déplacer une raquette **en fonction du temps** et l'**empêcher de sortir** du
  terrain ;
- créer la première version de la **scène de jeu** et la piloter au clavier ;
- écrire les **tests** qui prouvent que les bornes fonctionnent.

**Fichiers du projet :** `pong/paddle.py`, `pong/scenes/game.py`, `pong/settings.py`
**Test du projet :** `tests/test_paddle.py`

## 1. Le terrain de jeu

Avant de dessiner quoi que ce soit, décidons **où** les choses ont le droit
d'aller. On n'utilise pas toute la fenêtre : on réserve de la place.

```
 ┌───────────────────────────────────────────────┐  ← fenêtre 900 × 600
 │            bandeau de score (plus tard)        │
 │      ┌───────────────────────────────┐  ← FIELD_TOP (92)
 │      │ ▍                           ▐ │
 │      │            terrain            │  ← FIELD_HEIGHT (420)
 │      │ ▍                           ▐ │
 │      └───────────────────────────────┘  ← FIELD_BOTTOM (512)
 │   ↑                        ↑
 │ FIELD_LEFT (80)      FIELD_RIGHT (820)
 └───────────────────────────────────────────────┘
```

Ajoutez ces constantes à `pong/settings.py` :

```python
# --- Terrain de jeu ---
# Un rectangle à l'intérieur de la fenêtre : le haut laisse la place au bandeau
# de score, les côtés au décor. La balle et les raquettes y restent.
FIELD_LEFT = 80
FIELD_RIGHT = 820
FIELD_TOP = 92
FIELD_BOTTOM = 512
FIELD_WIDTH = FIELD_RIGHT - FIELD_LEFT
FIELD_HEIGHT = FIELD_BOTTOM - FIELD_TOP

# --- Raquette ---
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
PADDLE_INSET = 4            # écart entre le bord du terrain et la raquette
PADDLE_SPEED = 520          # pixels par seconde

# Couleurs néon
NEON_PINK = (255, 45, 149)
NEON_CYAN = (0, 229, 255)
```

> 💡 **Pourquoi des marges ?** Le jeu sera habillé (chapitre 11) : le haut
> accueillera le score, et les côtés un décor néon. Définir le terrain dès
> maintenant évite d'avoir à tout recalculer plus tard.

## 2. Une entité = des données + des méthodes

Une raquette, c'est :

- des **données** : sa position (`x`, `y`), sa taille (`width`, `height`), sa
  vitesse (`speed`) ;
- des **comportements** : se déplacer, se recentrer, connaître son rectangle.

C'est exactement ce qu'exprime une classe Python. Et comme cette logique
n'affiche rien, on pourra la tester **sans ouvrir de fenêtre**.

## 3. `pygame.Rect` : le rectangle qui sait tout faire

pygame fournit une classe très pratique, `pygame.Rect`, qui représente un
rectangle et sait :

- donner ses bords : `rect.left`, `rect.right`, `rect.top`, `rect.bottom` ;
- tester un chevauchement : `rect.colliderect(other)` ;
- être dessiné : `pygame.draw.rect(surface, couleur, rect)`.

Nous l'utiliserons surtout pour **dessiner** la raquette et, plus tard, pour
calculer les collisions.

> ⚠️ `Rect` travaille en **entiers**. Nos positions internes seront donc des
> nombres à virgule (`float`), et on ne convertira qu'au moment de dessiner :
> la physique reste fluide, l'affichage reste net.

## 4. La classe `Paddle`

```python
class Paddle:
    def __init__(self, x, speed=settings.PADDLE_SPEED, height=settings.PADDLE_HEIGHT):
        self.width = settings.PADDLE_WIDTH
        self.height = height
        self.speed = float(speed)
        self.x = float(x)
        self.y = settings.FIELD_TOP + (settings.FIELD_HEIGHT - height) / 2
```

La raquette naît **centrée verticalement** dans le terrain : on part du haut du
terrain (`FIELD_TOP`) et on descend de la moitié de l'espace restant.

```python
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def center_y(self):
        return self.y + self.height / 2
```

`@property` permet d'utiliser `paddle.rect` comme un attribut, alors que la
valeur est **recalculée** à chaque appel. Pratique : le rectangle suit toujours la
position courante, sans risque d'oubli de synchronisation.

## 5. Se déplacer, sans sortir

```python
    def move(self, direction, dt):
        """Déplace la raquette de `direction` (-1 haut, +1 bas) sur `dt` secondes."""
        self.move_by(direction * self.speed * dt)

    def move_by(self, delta):
        """Déplace la raquette de `delta` pixels, en la gardant à l'écran."""
        self.y += delta
        # Bornes : la raquette reste dans le terrain.
        self.y = max(float(settings.FIELD_TOP),
                     min(self.y, settings.FIELD_BOTTOM - self.height))
```

La ligne des bornes mérite qu'on s'y attarde :

```python
self.y = max(FIELD_TOP, min(self.y, FIELD_BOTTOM - self.height))
```

- `min(self.y, FIELD_BOTTOM - self.height)` : la raquette ne descend pas plus bas
  que le bas du terrain (son **bas** touche le bord, d'où le `- height`).
- `max(FIELD_TOP, ...)` : elle ne monte pas plus haut que le haut du terrain.
- Ensemble, ils **coincent** la valeur dans l'intervalle autorisé. C'est le
  « clamp », un réflexe à connaître.

Décomposer `move` en `move_by` a un avantage : le déplacement **brut** (en pixels)
sera réutilisé par l'IA, qui calcule elle-même sa distance (chapitre 06).

## 6. Contrôler au clavier

La raquette ne sait pas qu'un clavier existe : c'est la **scène** qui lit les
touches et lui dit de bouger. Rappelons les constantes du projet :

```python
# --- Contrôles (touches pygame) ---
# Joueur 1 : Z/S (AZERTY) et W/S (QWERTY) en secours.
P1_UP = (pygame.K_z, pygame.K_w)
P1_DOWN = (pygame.K_s,)
# Joueur 2 : flèches haut / bas.
P2_UP = (pygame.K_UP,)
P2_DOWN = (pygame.K_DOWN,)
# Navigation / actions.
KEY_MENU = (pygame.K_q, pygame.K_m)
```

On ne réagit pas à l'événement « touche pressée », mais à l'**état** du clavier à
chaque image :

```python
keys = pygame.key.get_pressed()
if keys[pygame.K_z]:
    ...
```

C'est essentiel : avec les événements, il faudrait gérer des répétitions et des
relâchements. Avec `get_pressed()`, maintenir la touche déplace la raquette en
continu, image après image. On multiplie par `dt`, et le mouvement est fluide.

## À vous de jouer !

1. Écrivez la classe `Paddle` (fichier `pong/paddle.py`).
2. **Écrivez d'abord les tests** : une raquette neuve est centrée, et elle ne sort
   jamais du terrain, même si on la pousse très loin.
3. Créez une première **`GameScene`** (`pong/scenes/game.py`) qui :
   - place une raquette à gauche et une à droite ;
   - lit le clavier et les déplace (joueur 1 : Z/S ou W/S ; joueur 2 : flèches) ;
   - dessine les deux raquettes en rectangles néon sur fond sombre ;
   - revient au menu avec `Q` ou `M`.
4. Déclarez `GameScene` dans `App._scenes` et lancez `python main.py`… puis
   remplacez temporairement la scène de départ par `"game"` pour la voir.

<details>
<summary>Un indice sur la méthode d'entrée</summary>

```python
keys = pygame.key.get_pressed()
if any(keys[k] for k in settings.P1_UP):
    paddle.move_up(dt)
elif any(keys[k] for k in settings.P1_DOWN):
    paddle.move_down(dt)
```

</details>

## Corrigé

### `pong/paddle.py`

```python
"""La raquette : déplacement borné à l'écran.

Positions en pixels, vitesse en pixels par seconde. Logique pure, testable
sans fenêtre (seul `pygame.Rect` est utilisé).
"""

import pygame

from . import settings


class Paddle:
    """Une raquette verticale contrôlée par un joueur ou par l'IA."""

    def __init__(self, x, speed=settings.PADDLE_SPEED, height=settings.PADDLE_HEIGHT):
        self.width = settings.PADDLE_WIDTH
        self.height = height
        self.speed = float(speed)
        self.x = float(x)
        self.y = settings.FIELD_TOP + (settings.FIELD_HEIGHT - height) / 2

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def center_y(self):
        return self.y + self.height / 2

    def reset(self):
        """Replace la raquette au centre vertical du terrain."""
        self.y = settings.FIELD_TOP + (settings.FIELD_HEIGHT - self.height) / 2

    def move(self, direction, dt):
        """Déplace la raquette de `direction` (-1 haut, +1 bas) sur `dt` secondes."""
        self.move_by(direction * self.speed * dt)

    def move_by(self, delta):
        """Déplace la raquette de `delta` pixels, en la gardant à l'écran."""
        self.y += delta
        # Bornes : la raquette reste dans le terrain.
        self.y = max(float(settings.FIELD_TOP),
                     min(self.y, settings.FIELD_BOTTOM - self.height))

    def move_up(self, dt):
        self.move(-1, dt)

    def move_down(self, dt):
        self.move(1, dt)
```

### `tests/test_paddle.py`

```python
"""Tests de la raquette : centrage, déplacement et bornes."""

from pong import settings
from pong.paddle import Paddle


def test_paddle_starts_centered_in_the_field():
    paddle = Paddle(settings.FIELD_LEFT)

    centered = settings.FIELD_TOP + (settings.FIELD_HEIGHT - paddle.height) / 2
    assert paddle.y == centered


def test_paddle_never_goes_above_the_field():
    paddle = Paddle(settings.FIELD_LEFT)

    paddle.move_by(-10_000)   # poussée absurde vers le haut

    assert paddle.y == settings.FIELD_TOP


def test_paddle_never_goes_below_the_field():
    paddle = Paddle(settings.FIELD_LEFT)

    paddle.move_by(10_000)    # poussée absurde vers le bas

    assert paddle.y == settings.FIELD_BOTTOM - paddle.height


def test_move_depends_on_elapsed_time():
    paddle = Paddle(settings.FIELD_LEFT)

    slow = Paddle(settings.FIELD_LEFT)
    slow.move(direction=1, dt=0.05)     # un dixième... non, 50 ms

    fast = Paddle(settings.FIELD_LEFT)
    fast.move(direction=1, dt=0.10)     # deux fois plus longtemps

    assert fast.y > slow.y > paddle.y


def test_reset_recenters_the_paddle():
    paddle = Paddle(settings.FIELD_LEFT)
    paddle.move_by(10_000)

    paddle.reset()

    assert paddle.y == settings.FIELD_TOP + (settings.FIELD_HEIGHT - paddle.height) / 2
```

Lancez `pytest` : les tests passent. Notez au passage que **ces tests n'ouvrent
aucune fenêtre** — c'est tout l'intérêt d'avoir séparé la logique de l'affichage.

### `pong/scenes/game.py` (première version)

```python
"""La partie : première version (raquettes mobiles)."""

import pygame

from .. import settings
from ..paddle import Paddle
from .base import Scene

# Couleur du fond de la partie (sera remplacée par le décor au chapitre 11).
BACKGROUND_COLOR = (10, 12, 24)


class GameScene(Scene):
    """Une partie, avec deux raquettes contrôlées au clavier."""

    def __init__(self, app, mode="1p"):
        super().__init__(app)
        self.mode = mode
        self.left_paddle = Paddle(settings.FIELD_LEFT + settings.PADDLE_INSET)
        self.right_paddle = Paddle(
            settings.FIELD_RIGHT - settings.PADDLE_INSET - settings.PADDLE_WIDTH)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in settings.KEY_MENU:
            self.app.switch_scene("menu")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self._control(self.left_paddle, keys, settings.P1_UP, settings.P1_DOWN, dt)
        if self.mode == "2p":
            self._control(self.right_paddle, keys, settings.P2_UP, settings.P2_DOWN, dt)

    def _control(self, paddle, keys, up, down, dt):
        """Déplace `paddle` selon les touches maintenues."""
        if any(keys[k] for k in up):
            paddle.move_up(dt)
        elif any(keys[k] for k in down):
            paddle.move_down(dt)

    def draw(self, surface):
        surface.fill(BACKGROUND_COLOR)
        pygame.draw.rect(surface, settings.NEON_CYAN, self.left_paddle.rect)
        pygame.draw.rect(surface, settings.NEON_PINK, self.right_paddle.rect)
```

### `pong/app.py` (la ligne qui change)

Dans `App.__init__`, enregistrez la nouvelle scène :

```python
from .scenes.game import GameScene
...
        self._scenes = {"menu": MenuScene, "game": GameScene}
```

Pour l'essayer immédiatement, terminez `__init__` par :

```python
        self.switch_scene("game", mode="2p")
```

Z/S déplacent la raquette de gauche, les flèches celle de droite, `Q` revient au
menu. **Vous avez un jeu qui bouge !**

> **Dans le projet de référence :** `pong/paddle.py` est identique à ce corrigé.
> La vraie `GameScene` est enrichie au fil des chapitres suivants.

## En résumé

- Une entité = **des données + des méthodes** (`Paddle`).
- `pygame.Rect` sert à dessiner et, plus tard, à détecter les collisions.
- On déplace avec `vitesse × dt` : la vitesse est en pixels par seconde.
- Le « clamp » (`max(borne_min, min(valeur, borne_max))`) garde la raquette dans
  le terrain.
- Le clavier se lit **par état** (`pygame.key.get_pressed()`), pas par événement.
- La logique pure se teste **sans fenêtre**.

## Étape suivante

→ [04 — La balle](04-la-balle.md)
