# 05 — Les collisions

## Objectifs

À la fin de ce chapitre, vous saurez :

- détecter le contact entre un **cercle** (la balle) et un **rectangle** (la raquette) ;
- pourquoi la détection par « boîte englobante » **rate** les contacts sur un coin ;
- calculer une **normale** et une **pénétration** pour repousser proprement la balle ;
- éviter le **« tunneling »** (la balle qui traverse une raquette) grâce aux
  sous-étapes ;
- écrire le **test de non-régression** qui reproduit le bug du coin.

**Fichiers du projet :** `pong/collision.py`, `pong/scenes/game.py`
**Test du projet :** `tests/test_collision.py`, `tests/test_game_scene.py`

## 1. Le problème

La balle rebondit sur les murs, mais passe encore à travers les raquettes. Il faut
détecter le contact. Question simple, en apparence : « est-ce que la balle touche
le rectangle ? »

## 2. La tentation : les boîtes englobantes

pygame propose une méthode séduisante : `rect.colliderect(other)`. Elle compare
deux rectangles. Comme la balle possède un `rect` (son carré englobant), on
écrirait :

```python
if ball.rect.colliderect(paddle.rect):
    ...
```

C'est simple… et **faux**. Deux problèmes :

1. **Le carré n'est pas un cercle.** Aux coins, le carré de la balle touche le
   rectangle alors que la balle (le disque) ne le touche **pas encore** — on
   déclenche un rebond « dans le vide ».
2. **L'inégalité est stricte.** Quand le carré de la balle est exactement
   **tangent** au bord de la raquette, `colliderect` renvoie `False` : le contact
   réel est **raté**. C'est précisément le bug que ce chapitre corrige : la balle
   traversait la raquette quand elle l'effleurait sur un coin.

> 🐞 **Le bug du coin.** Un contact manqué une seule image, et la balle se retrouve
> de l'autre côté de la raquette. Ce genre de défaut est intermittent (il dépend de
> la vitesse et de l'angle), donc pénible à reproduire… et c'est exactement
> pourquoi on écrit un **test** qui le reproduit.

## 3. La bonne modélisation : un cercle contre un rectangle

On modélise la balle comme un **cercle** de centre `(cx, cy)` et de rayon `r`, et
la raquette comme un rectangle. La détection exacte se fait en trois temps :

**① Trouver le point du rectangle le plus proche du centre.**

```
        ┌──────────────┐
        │              │
        │         ●    │  ← le centre du cercle
        │         ↑    │
        │      point le│ plus proche
        └──────────────┘
```

On « coince » les coordonnées du centre dans les bornes du rectangle :

```python
nearest_x = max(rect.left, min(cx, rect.right))
nearest_y = max(rect.top,  min(cy, rect.bottom))
```

**② Mesurer la distance** entre le centre et ce point :

```python
dx = cx - nearest_x
dy = cy - nearest_y
dist2 = dx * dx + dy * dy
```

**③ Comparer au rayon.** Il y a contact si `dist2 <= r²` :

```
      dist > r            dist = r            dist < r
   ●                   ●                   ●
        ┌────┐            ┌────┐              ┌────┐
        │    │            │    │              │    │
        └────┘            └────┘              └────┘
   pas de contact      contact (tangent)   pénétration
```

## 4. Normale et pénétration

Quand il y a contact, on a besoin de **deux informations** pour réagir :

- la **normale** : la direction à suivre pour sortir du rectangle (du point le
  plus proche vers le centre du cercle, normalisée en longueur 1) ;
- la **pénétration** : de combien il faut reculer pour ne plus se chevaucher.

```python
dist = math.sqrt(dist2)
normale = (dx / dist, dy / dist)
penetration = radius - dist
```

> 💡 Si le centre du cercle est **dans** le rectangle, `dx = dy = 0` : on ne peut pas
> normaliser. On choisit alors une direction de secours (`(0, -1)`, vers le haut).
> Ce cas ne se produit pas dans notre jeu (la scène traite d'abord la face
> latérale), mais mieux vaut un contrat explicite qu'un plantage.

## 5. `circle_rect_contact`

Ce calcul n'a besoin ni de pygame ni d'une fenêtre : c'est de la géométrie pure,
donc **testable**. On l'isole dans `pong/collision.py`.

## 6. Résoudre la collision dans la scène

Détecter ne suffit pas : il faut **repositionner** la balle, sinon elle resterait
engagée dans la raquette et déclencherait un rebond à chaque image.

Deux cas à distinguer :

```
   ┌────┐
   │    │        ① FACE : la balle arrive sur le côté plat.
   │  ● │           → on la replace juste devant, et l'angle dépend
   │    │             du point d'impact.
   └────┘
                      ② COIN : la balle touche un coin haut ou bas.
        ●                → on la repousse le long de la normale.
```

```python
if rect.top <= ball.y <= rect.bottom:
    # Face latérale : rebond horizontal.
    ball.x = rect.right + ball.radius if direction > 0 else rect.left - ball.radius
else:
    # Coin : on ressort la balle le long de la normale.
    ball.x += normal_x * penetration
    ball.y += normal_y * penetration
```

On ne teste la collision que si la balle **se dirige vers** la raquette
(`ball.vx * direction >= 0` → on saute). Sinon, une balle qui vient de rebondir
serait « rattrapée » par la même raquette et resterait collée.

## 7. Le « tunneling » : quand le temps va trop vite

À chaque image, la balle avance de `v × dt`. Si elle est très rapide et l'image
longue, elle peut parcourir **plus que l'épaisseur de la raquette** en une seule
étape :

```
   image N                    image N+1
   ●  ─────────────────────────────▶        ●      (la raquette ▐ est sautée !)
```

C'est le **tunneling**. La parade : découper le déplacement en **sous-étapes** dont
chacune ne dépasse pas le rayon de la balle.

```python
distance = max(abs(self.ball.vx), abs(self.ball.vy)) * dt
steps = max(1, int(distance / self.ball.radius) + 1)
sub_dt = dt / steps

for _ in range(steps):
    self.ball.update(sub_dt)
    ...   # murs, raquettes, sortie : on teste À CHAQUE sous-étape
```

Le coût est négligeable (quelques étapes de plus), et le bug disparaît.

## À vous de jouer !

1. Écrivez `pong/collision.py` avec `circle_rect_contact(cx, cy, radius, rect)`.
2. Écrivez les tests **avant** :
   - un cercle loin du rectangle → `None` ;
   - un cercle qui touche la face → une normale horizontale ;
   - un cercle **tangent** au bord → un contact (c'est le bug du coin : la boîte
     englobante répondrait `False` ici) ;
   - un cercle qui chevauche un **coin** → une normale oblique ;
   - un cercle à l'intérieur → une normale de secours.
3. Branchez la collision dans `GameScene` (`_handle_paddles`, `_resolve_paddle`) et
   ajoutez les sous-étapes dans la mise à jour de la balle.
4. Écrivez un **test de non-régression** : une balle qui frôle le coin d'une
   raquette ne doit **jamais** la traverser.

<details>
<summary>Un indice sur la tangence</summary>

Un cercle de rayon `r` centré à `cx = rect.left - r` (donc **juste** à gauche du
rectangle) a `dist2 == r²`. Le contact existe : la fonction doit renvoyer une
normale, pas `None`. Utilisez `<=` dans la comparaison, pas `<`.

</details>

## Corrigé

### `pong/collision.py`

```python
"""Détection de collision cercle / rectangle.

La balle est modélisée par un cercle, la raquette par un `pygame.Rect`. Ces
fonctions sont pures et testables sans écran. Elles remplacent la détection
« boîte englobante » (`Rect.colliderect`), qui rate les contacts sur un coin
lorsque le carré de la balle est seulement tangent à la raquette.
"""

import math


def circle_rect_contact(cx, cy, radius, rect):
    """Contact entre le cercle (cx, cy, radius) et le rectangle `rect`.

    Renvoie `((nx, ny), penetration)` si le cercle touche le rectangle, sinon
    `None`. `(nx, ny)` est la normale unitaire allant du rectangle vers le
    centre du cercle ; `penetration` est la profondeur de chevauchement.
    """
    nearest_x = max(rect.left, min(cx, rect.right))
    nearest_y = max(rect.top, min(cy, rect.bottom))
    dx = cx - nearest_x
    dy = cy - nearest_y
    dist2 = dx * dx + dy * dy
    if dist2 > radius * radius:
        return None
    if dist2 == 0.0:
        # Centre à l'intérieur du rectangle : on repousse vers le haut.
        return (0.0, -1.0), float(radius)
    dist = math.sqrt(dist2)
    return (dx / dist, dy / dist), radius - dist
```

### `tests/test_collision.py`

```python
"""Tests de la détection cercle / rectangle."""

import pygame

from pong.collision import circle_rect_contact

RECT = pygame.Rect(100, 100, 20, 60)   # une raquette verticale


def test_far_away_circle_does_not_touch():
    assert circle_rect_contact(0, 0, 8, RECT) is None


def test_circle_touching_the_flat_side():
    contact = circle_rect_contact(RECT.left - 8, 130, 8, RECT)

    assert contact is not None
    (nx, ny), penetration = contact
    assert nx == -1 and ny == 0          # normale horizontale, vers la gauche
    assert penetration == 0


def test_tangent_circle_is_a_contact():
    """Le cas que la boîte englobante ratait (bug du coin)."""
    contact = circle_rect_contact(RECT.left, RECT.top - 8, 8, RECT)

    assert contact is not None


def test_circle_on_the_corner_gets_a_diagonal_normal():
    contact = circle_rect_contact(RECT.left - 6, RECT.top - 6, 8, RECT)

    assert contact is not None
    (nx, ny), _ = contact
    assert nx < 0 and ny < 0             # normale oblique (vers le haut-gauche)


def test_center_inside_gets_a_fallback_normal():
    (nx, ny), penetration = circle_rect_contact(110, 130, 8, RECT)

    assert (nx, ny) == (0.0, -1.0)
```

### Le branchement dans `GameScene`

```python
from ..collision import circle_rect_contact
...

    def _advance_ball(self, dt):
        # Sous-étapes : la balle ne doit jamais avancer de plus que son rayon en
        # une étape, sinon elle pourrait traverser une raquette (« tunneling »).
        distance = max(abs(self.ball.vx), abs(self.ball.vy)) * dt
        steps = max(1, int(distance / self.ball.radius) + 1)
        sub_dt = dt / steps

        for _ in range(steps):
            self.ball.update(sub_dt)
            self.ball.handle_walls()
            if self._handle_paddles():
                break
            if self.ball.off_screen() is not None:
                break

    def _handle_paddles(self):
        """Renvoie True si une collision balle/raquette a été traitée."""
        if self._resolve_paddle(self.left_paddle, direction=1):
            return True
        if self._resolve_paddle(self.right_paddle, direction=-1):
            return True
        return False

    def _resolve_paddle(self, paddle, direction):
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
```

### `tests/test_game_scene.py` — le test de non-régression

```python
def test_ball_bounces_when_touching_the_paddle_corner():
    """Une balle qui frôle un coin ne doit pas traverser la raquette."""
    app = App(sound_enabled=False)
    app.switch_scene("game", mode="2p")
    scene = app.scene

    paddle = scene.right_paddle
    ball = scene.ball
    # La balle arrive sur le coin haut de la raquette.
    ball.x = paddle.rect.left - ball.radius + 1
    ball.y = paddle.rect.top - ball.radius + 1
    ball.speed = 500
    ball.bounce_off_paddle(paddle.center_y, direction=1)
    ball.vx = -abs(ball.vx)          # … non : elle doit aller VERS la raquette
    ball.vx = -ball.speed            # vers la gauche, donc vers la raquette droite

    scene._resolve_paddle(paddle, direction=-1)

    assert ball.x <= paddle.rect.left - ball.radius + 1   # repoussée à gauche
```

> 💡 Écrivez ce test **avant** d'écrire `_resolve_paddle`. Vous le verrez échouer
> (la balle traverse), puis passer après la correction. C'est votre assurance
> contre le retour du bug.

La balle rebondit désormais sur les raquettes, coins compris. Il manque encore un
adversaire pour la raquette de droite : l'IA.

> **Dans le projet de référence :** `pong/collision.py` est identique. Le
> sous-échantillonnage (`_advance_ball`) y est expliqué par le même commentaire.

## En résumé

- **N'utilisez pas** `Rect.colliderect` pour un cercle : elle rate les contacts au
  coin (inégalité stricte), et se trompe aux angles.
- Cercle/rectangle : on mesure la distance au **point le plus proche**, puis on la
  compare au rayon (`<=`, pas `<`).
- On résout la collision en **repositionnant** la balle (face : devant la raquette ;
  coin : le long de la normale).
- Les **sous-étapes** éliminent le tunneling.
- Un test de non-régression transforme un bug intermittent en garde-fou permanent.

## Étape suivante

→ [06 — L'IA](06-lia.md)
