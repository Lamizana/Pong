# 07 — Le score et la victoire

Il faut compter les points et savoir quand la partie s'arrête. C'est une logique
minuscule, mais qui mérite son propre module — et ses propres tests.

## La classe `Score`

```python
from .settings import POINTS_TO_WIN


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

Deux choix de conception à noter :

- `points_to_win` est un **paramètre**, pas une valeur figée. En jeu on utilise 7 (la
  constante), mais les tests peuvent instancier `Score(points_to_win=2)` pour aller
  vite à la victoire.
- On distingue un camp **gauche** (`"left"`, le joueur 1) et **droit** (`"right"`,
  le joueur 2 ou l'IA).

## Tester les règles

```python
def test_no_winner_before_target():
    score = Score(points_to_win=3)
    score.add_point("left")
    score.add_point("left")
    assert score.winner() is None


def test_reaching_target_declares_winner():
    score = Score(points_to_win=3)
    winner = None
    for _ in range(3):
        winner = score.add_point("left")
    assert winner == "left"
```

On couvre aussi le cas d'erreur :

```python
def test_invalid_side_raises_value_error():
    score = Score()
    with pytest.raises(ValueError):
        score.add_point("middle")
```

## Qui marque, et où va la balle ensuite ?

La balle sortie **à gauche** a dépassé la raquette gauche : le camp **droit** marque.
Et inversement. Dans la scène de jeu :

```python
side = self.ball.off_screen()
if side is None:
    return

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
```

Détail intéressant : `add_point` **renvoie** le vainqueur (ou `None`). Cela permet de
gérer le score et la fin de partie en un seul point d'appel, sans avoir à
re-interroger `winner()`.

## La remise en jeu

Après chaque point :

1. La balle revient au centre (`ball.reset`), avec une petite direction aléatoire.
2. Un **délai d'une seconde** (`serve_timer`) laisse le temps aux joueurs de se
   préparer. Pendant ce temps, la balle ne bouge pas — mais **les raquettes restent
   contrôlables**, pour se repositionner avant le service.
3. Les raquettes sont recentrées.

```python
def update(self, dt):
    keys = pygame.key.get_pressed()
    self._move_players(keys, dt)
    if self.ai is not None:
        self.ai.update(self.ball.y, self.right_paddle, dt)

    if self.serve_timer > 0:
        self.serve_timer -= dt
        return          # la balle n'avance pas, mais les raquettes restent mobiles

    self._advance_ball(dt)
```

La balle est relancée vers le camp qui a encaissé le point — une convention
courante et équitable.

## Afficher le score

Dans `scenes/game.py` :

```python
def _draw_scores(self, surface):
    center_x = settings.WINDOW_WIDTH // 2
    self.app.draw_text(surface, str(self.score.left), self.app.font_large,
                       settings.WHITE, center=(center_x - 80, 60))
    self.app.draw_text(surface, str(self.score.right), self.app.font_large,
                       settings.WHITE, center=(center_x + 80, 60))
```

Le score de gauche est affiché à gauche du centre, celui de droite à droite. Le
filet central sépare visuellement les deux.

## Étape suivante

→ [08 — Le menu et les scènes](08-le-menu-et-les-scenes.md)
