# 06 — L'IA

En mode un joueur, une **IA** contrôle la raquette de droite. Le défi n'est pas de
faire une IA imbattable, mais une IA **intéressante** : elle doit bien jouer, tout en
restant battable. Sinon, le jeu n'est pas amusant.

## Deux leviers pour régler la difficulté

Notre IA est volontairement simple. Elle vise la balle et se déplace vers elle. Pour
créer des niveaux, on règle deux paramètres :

- **`speed`** : la vitesse maximale de la raquette. Lente, l'IA ne suit pas les
  balles rapides.
- **`error`** : une imprécision de visée. L'IA vise la balle **décalée** d'une
  distance aléatoire bornée par `error`. Une IA parfaite au centre serait pénible ;
  viser à côté la rend humaine.

```python
AI_LEVELS = {
    "facile":    {"speed": 300, "error": 70, "label": "Facile"},
    "moyen":     {"speed": 440, "error": 35, "label": "Moyen"},
    "difficile": {"speed": 640, "error": 8,  "label": "Difficile"},
}
```

Facile est lente et imprécise ; difficile est rapide et quasi exacte.

## La classe `AI`

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

Note le paramètre `rng` : on peut injecter un générateur aléatoire. Dans les tests, on
lui passe `random.Random(42)` (graine fixe) pour obtenir un comportement
**reproductible**. En jeu, on laisse le hasard normal.

## Viser avec une marge d'erreur

L'écart de visée est retiré **une fois par échange**, pas à chaque image — sinon l'IA
tremblerait. On le renouvelle après chaque coup de raquette :

```python
def randomize_offset(self):
    self.target_offset = self._rng.uniform(-self.error, self.error)
```

`uniform(-e, e)` tire un nombre au hasard uniformément entre `-e` et `+e`.

## Le déplacement

```python
def update(self, ball_y, paddle, dt):
    target = ball_y + self.target_offset
    diff = target - paddle.center_y
    if abs(diff) <= settings.AI_DEAD_ZONE:
        return                                       # assez proche : on ne bouge pas
    direction = 1 if diff > 0 else -1
    step = min(abs(diff), self.speed * dt)           # jamais plus vite que la limite
    paddle.move_by(direction * step)
```

Trois idées importantes :

1. **La cible** est la position de la balle, décalée par `target_offset`.
2. **La vitesse est bornée** : `step` ne peut pas dépasser `speed * dt`. C'est ce qui
   rend l'IA « facile » réellement plus lente, même face à une balle rapide.
3. **La zone morte** (`AI_DEAD_ZONE`, quelques pixels) évite que l'IA oscille sans
   arrêt autour de la cible.

## Tester l'IA

```python
def test_moves_down_when_target_is_below():
    ai = AI(level="moyen")
    ai.target_offset = 0.0
    paddle = Paddle(x=30)
    paddle.y = 100
    ai.update(ball_y=300, paddle=paddle, dt=0.1)
    assert paddle.y > 100


def test_step_is_limited_by_ai_speed():
    ai = AI(level="facile")
    paddle = Paddle(x=30)
    paddle.y = 0.0
    ai.update(ball_y=100000, paddle=paddle, dt=0.1)
    assert paddle.y <= ai.speed * 0.1 + 1e-6


def test_randomize_offset_stays_within_error():
    ai = AI(level="facile", rng=random.Random(42))
    for _ in range(50):
        ai.randomize_offset()
        assert abs(ai.target_offset) <= ai.error
```

Le deuxième test garantit que, même si la balle est très loin, l'IA ne « téléporte »
pas sa raquette : elle avance au maximum à `speed * dt`.

## Équilibrage

Les valeurs de `AI_LEVELS` ne sont pas gravées dans le marbre. Après quelques parties,
ajuste-les :

- L'IA facile vous met-elle en difficulté ? Baisse `speed` ou monte `error`.
- L'IA difficile est-elle trop faible ? Monte `speed` ou baisse `error`.

C'est tout l'intérêt d'avoir centralisé ces réglages dans `settings.py`.

## Étape suivante

→ [07 — Le score et la victoire](07-score-et-victoire.md)
