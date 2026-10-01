# 04 — Les raquettes

Passons aux premières entités du jeu. Une **raquette** est un rectangle vertical qui
se déplace vers le haut ou vers le bas, sans jamais sortir de l'écran.

## Représenter la raquette

En pygame, un rectangle se décrit avec `pygame.Rect(x, y, largeur, hauteur)`, où
`(x, y)` est le coin **haut-gauche**. Mais pour raisonner sur une raquette, on pense
plutôt à sa position et à son **centre**. Stockons donc simplement `x`, `y`, et
exposons un `rect` à la demande :

```python
import pygame
from . import settings


class Paddle:
    def __init__(self, x, speed=settings.PADDLE_SPEED, height=settings.PADDLE_HEIGHT):
        self.width = settings.PADDLE_WIDTH
        self.height = height
        self.speed = float(speed)
        self.x = float(x)
        self.y = (settings.WINDOW_HEIGHT - height) / 2   # centrée verticalement

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def center_y(self):
        return self.y + self.height / 2
```

- `@property` transforme une méthode en attribut calculé : on écrit `paddle.rect`
  et non `paddle.rect()`.
- `center_y` nous servira pour calculer l'angle de rebond de la balle (chapitre 05).

## Déplacer la raquette

L'idée clé : un **unique** point de vérité pour le déplacement, `move_by(delta)`, qui
applique le décalage **et** borne la position. Les autres méthodes s'appuient dessus.

```python
def move(self, direction, dt):
    """direction : -1 = haut, +1 = bas."""
    self.move_by(direction * self.speed * dt)

def move_by(self, delta):
    self.y += delta
    # On borne la raquette dans l'écran.
    self.y = max(0.0, min(self.y, settings.WINDOW_HEIGHT - self.height))

def move_up(self, dt):
    self.move(-1, dt)

def move_down(self, dt):
    self.move(1, dt)
```

Pourquoi cette factorisation ? Parce que l'IA (chapitre 06) a besoin de déplacer la
raquette d'une distance **précise**, pas d'une fraction de `dt`. En centralisant la
logique dans `move_by`, on garantit que les bornes sont respectées dans tous les cas.

## Écrire le test d'abord

En TDD, on commence par décrire le comportement attendu. Voici un extrait de
`tests/test_paddle.py` :

```python
def test_initial_position_is_centered_vertically():
    paddle = Paddle(x=30)
    assert paddle.center_y == pytest.approx(settings.WINDOW_HEIGHT / 2)


def test_cannot_leave_bottom_of_screen():
    paddle = Paddle(x=30)
    paddle.move_down(100)          # un déplacement énorme
    assert paddle.y == pytest.approx(settings.WINDOW_HEIGHT - paddle.height)


def test_movement_respects_dt_and_speed():
    paddle = Paddle(x=30, speed=100)
    start = paddle.y
    paddle.move_down(0.25)         # 0,25 s à 100 px/s = 25 px
    assert paddle.y == pytest.approx(start + 25)
```

On lance le test **avant** d'écrire la classe : il échoue avec
`ModuleNotFoundError: No module named 'pong.paddle'`. On implémente ensuite le
minimum pour le faire passer au vert. On ne teste jamais du code après coup : un test
qu'on n'a pas vu échouer ne prouve rien.

> `pytest.approx` compare des nombres flottants avec une tolérance. On l'utilise
> systématiquement pour éviter les faux échecs dus aux arrondis.

## Où placer les raquettes ?

Les deux raquettes sont symétriques. On calcule leur position `x` à partir des
constantes :

```python
left_x = settings.PADDLE_MARGIN
right_x = settings.WINDOW_WIDTH - settings.PADDLE_MARGIN - settings.PADDLE_WIDTH
```

Avec une marge de 30 px et une largeur de 15 px, la raquette gauche occupe
`x = 30`, la droite `x = 855` sur un écran de 900 px.

## Contrôler les raquettes au clavier

Au chapitre 03, nous réagissions aux événements ponctuels (`KEYDOWN`). Pour un
déplacement continu, il vaut mieux interroger l'état **maintenu** des touches à chaque
image :

```python
keys = pygame.key.get_pressed()
if any(keys[key] for key in settings.P1_UP):
    self.left_paddle.move_up(dt)
if any(keys[key] for key in settings.P1_DOWN):
    self.left_paddle.move_down(dt)
```

Les touches sont définies dans `settings.py`, ce qui permet d'accepter plusieurs
variantes (AZERTY **Z/S** et QWERTY **W/S**) sans toucher à la logique :

```python
P1_UP = (pygame.K_z, pygame.K_w)
P1_DOWN = (pygame.K_s,)
P2_UP = (pygame.K_UP,)
P2_DOWN = (pygame.K_DOWN,)
```

- **Joueur 1** : `Z` / `S` (ou `W` / `S`).
- **Joueur 2** : flèches `↑` / `↓`.

En mode 1 joueur, seule la raquette gauche est contrôlée : la droite appartient à
l'IA. En mode 2 joueurs, les deux répondent au clavier.

## Étape suivante

→ [05 — La balle et la physique](05-la-balle-et-la-physique.md)
