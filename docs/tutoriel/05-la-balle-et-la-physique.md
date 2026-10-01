# 05 — La balle et la physique

La balle est le cœur du jeu. Deux choses à gérer : son **déplacement** et ses
**rebonds**. C'est aussi le chapitre le plus « mathématique », mais rassure-toi :
tout tient en quelques formules simples.

## Position et vitesse

On représente la balle par sa position (`x`, `y`, le centre) et un **vecteur
vitesse** (`vx`, `vy`) exprimé en pixels par seconde.

```python
class Ball:
    def __init__(self, x=None, y=None, speed=settings.BALL_START_SPEED):
        self.x = settings.WINDOW_WIDTH / 2 if x is None else float(x)
        self.y = settings.WINDOW_HEIGHT / 2 if y is None else float(y)
        self.radius = settings.BALL_RADIUS
        self.speed = float(speed)     # norme de la vitesse
        self.vx = 0.0
        self.vy = 0.0
```

On garde `speed` (la **norme**) à part de `(vx, vy)` (la **direction**). C'est très
pratique : la vitesse augmente à chaque échange, mais l'angle se calcule
indépendamment.

## Déplacement

```python
def update(self, dt):
    self.x += self.vx * dt
    self.y += self.vy * dt
```

Rappel du chapitre 03 : `dt` en secondes garantit un mouvement identique à 60 ou
144 images par seconde.

## Rebond sur les murs haut et bas

Quand la balle touche le bord supérieur ou inférieur, il suffit **d'inverser** `vy`
et de replacer la balle juste à l'intérieur (pour éviter qu'elle ne colle au mur) :

```python
def handle_walls(self):
    if self.vy < 0 and self.y - self.radius <= 0:      # va vers le haut
        self.y = self.radius
        self.vy = -self.vy                             # repart vers le bas
        return True
    if self.vy > 0 and self.y + self.radius >= settings.WINDOW_HEIGHT:
        self.y = settings.WINDOW_HEIGHT - self.radius
        self.vy = -self.vy                             # repart vers le haut
        return True
    return False
```

On ne corrige que si la balle se dirige **vers** le mur. Sans ce garde-fou, une balle
immobile (`vy == 0`) placée contre un bord « collerait » au mur en rebondissant sans
fin.

La méthode renvoie `True` quand un rebond a eu lieu : la scène de jeu s'en sert pour
jouer le son correspondant.

## Le rebond « avancé » sur la raquette

C'est la partie intéressante. Un Pong basique renvoie la balle avec un angle fixe :
le jeu est vite lassant. Nous voulons que **l'angle dépende de l'endroit où la balle
frappe la raquette**.

```
        raquette
          │
  haut    │  ← frappe en haut  → la balle part vers le haut
          │
  centre  │  ← frappe au centre → la balle repart à l'horizontale
          │
  bas     │  ← frappe en bas   → la balle part vers le bas
          │
```

On calcule d'abord la position relative de l'impact :

```python
half = settings.PADDLE_HEIGHT / 2
offset = (self.y - paddle_center_y) / half     # -1 (haut) … 0 (centre) … +1 (bas)
offset = max(-1.0, min(1.0, offset))           # on borne l'écart
```

Puis on convertit cet écart en angle, entre `-60°` et `+60°` :

```python
angle = math.radians(settings.MAX_BOUNCE_ANGLE * offset)
self.vx = direction * self.speed * math.cos(angle)
self.vy = self.speed * math.sin(angle)
```

- `direction` vaut `+1` quand la balle repart vers la droite, `-1` vers la gauche.
- `cos` donne la composante horizontale, `sin` la composante verticale.
- Au centre (`offset = 0`), on a `cos(0) = 1` et `sin(0) = 0` : la balle repart bien
  à l'horizontale.

Le module `math` travaille en **radians** : d'où la conversion avec
`math.radians(...)`.

## L'accélération progressive

Pour intensifier les échanges, la vitesse augmente un peu à chaque coup de raquette,
sans dépasser un plafond :

```python
self.speed = min(self.speed + settings.BALL_SPEEDUP, settings.BALL_MAX_SPEED)
```

## Détecter la sortie de terrain

Un point est marqué quand la balle quitte l'écran. On teste les deux côtés :

```python
def off_screen(self):
    if self.x + self.radius < 0:
        return "left"
    if self.x - self.radius > settings.WINDOW_WIDTH:
        return "right"
    return None
```

## La détection de collision

Au chapitre 08 (scène de jeu), on utilisera `pygame.Rect.colliderect` pour savoir si
la balle touche une raquette. On expose pour cela un rectangle de collision :

```python
@property
def rect(self):
    size = self.radius * 2
    return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), size, size)
```

### Éviter la traversée (« tunneling »)

Une détection image par image a une limite : si la balle se déplace de plus que
l'épaisseur de la raquette en une seule image, elle peut « sauter » par-dessus sans
jamais être détectée. Avec une vitesse maximale de 820 px/s et une image lente de
50 ms, cela représente jusqu'à **41 pixels** — bien plus que la largeur d'une raquette
(15 px).

La scène de jeu découpe donc chaque image en **sous-pas** : on avance la balle par
petits bonds ne dépassant jamais son rayon, et l'on teste la collision à chaque
sous-pas.

```python
distance = max(abs(self.ball.vx), abs(self.ball.vy)) * dt
steps = max(1, int(distance / self.ball.radius) + 1)
sub_dt = dt / steps
for _ in range(steps):
    self.ball.update(sub_dt)
    if self.ball.handle_walls():
        self.app.sound.wall_bounce()
    if self._handle_paddles():
        break
```

Quelques lignes qui éliminent une classe entière de bugs frustrants (« j'avais bien
placé ma raquette, mais le point a été compté ! »).

## Tester la physique

Comme la physique ne dépend pas de l'affichage, elle se teste directement. Extrait de
`tests/test_ball.py` :

```python
def test_update_moves_according_to_velocity():
    ball = Ball()
    ball.x, ball.y = 100.0, 100.0
    ball.vx, ball.vy = 60.0, -30.0
    ball.update(0.5)
    assert ball.x == pytest.approx(130.0)
    assert ball.y == pytest.approx(85.0)


def test_hit_paddle_center_goes_straight():
    ball = Ball()
    ball.y = 300.0
    ball.bounce_off_paddle(paddle_center_y=300.0, direction=1)
    assert ball.vy == pytest.approx(0.0, abs=1e-6)
    assert ball.vx == pytest.approx(settings.BALL_START_SPEED)


def test_max_bounce_angle_is_clamped():
    ball = Ball()
    ball.y = 300.0 - 5000            # très au-dessus : l'angle doit être borné
    ball.bounce_off_paddle(paddle_center_y=300.0, direction=1)
    angle = math.degrees(math.atan2(abs(ball.vy), abs(ball.vx)))
    assert angle == pytest.approx(settings.MAX_BOUNCE_ANGLE, abs=0.5)
```

Ce dernier test est important : même si la balle frappe très loin du centre, l'angle
ne doit jamais dépasser `MAX_BOUNCE_ANGLE`, sinon la balle repartirait presque à la
verticale et le jeu serait injouable.

## Étape suivante

→ [06 — L'IA](06-lia.md)
