# 09 — Les sons et la pause

## Objectifs

À la fin de ce chapitre, vous saurez :

- **générer** un son en Python, sans aucun fichier audio ;
- construire un buffer PCM exploitable par pygame ;
- concevoir un module de son qui **se dégrade proprement** quand l'audio n'existe
  pas (CI, machine sans carte son) ;
- créer un écran de **pause** qui fige la partie et sait la **reprendre**.

**Fichiers du projet :** `pong/sound.py`, `pong/scenes/pause.py`, `pong/settings.py`
**Test du projet :** `tests/test_sound.py`

## 1. Un son, c'est une suite de nombres

Un son numérique est une suite d'**échantillons** (des nombres) décrivant une onde.
Une note pure est une **sinusoïde** :

```
   amplitude
      │    ╭─╮         ╭─╮
      │  ╱   ╲       ╱   ╲
   ───┼─╯     ╰─────╯     ╰──────▶ temps
      │
```

Pour produire une note de fréquence `f` pendant `d` millisecondes, on calcule :

```
échantillon(i) = amplitude × sin(2π × f × i / sample_rate)
```

- `sample_rate` : le nombre d'échantillons par seconde (44 100, la qualité CD) ;
- `i` : le numéro de l'échantillon ;
- `i / sample_rate` : le temps écoulé, en secondes.

Ajoutez à `settings.py` :

```python
# --- Sons ---
SOUND_SAMPLE_RATE = 44100
SOUND_VOLUME = 0.4
SOUND_HIT_FREQ = 440        # raquette
SOUND_WALL_FREQ = 300       # mur
SOUND_SCORE_FREQ = 200      # point marqué
SOUND_WIN_FREQ = 660        # victoire
SOUND_DURATION_MS = 90
```

Chaque bruitage a sa **fréquence** : aiguë pour la raquette, grave pour le point,
plus aiguë encore pour la victoire.

## 2. Du Python à pygame : le buffer PCM

pygame attend un **buffer** : une suite d'octets. On la construit avec `array` :

```python
import array

samples = array.array("h")       # « h » = entier signé 16 bits
samples.append(value)            # canal gauche
samples.append(value)            # canal droit
return samples.tobytes()
```

- **16 bits signés** : chaque échantillon va de -32767 à +32767. C'est le format
  demandé par `pygame.mixer.init(size=-16, channels=2)`.
- **stéréo** : on écrit deux fois la même valeur (gauche et droite).

## 3. Le fondu : éviter le « clic »

Couper une sinusoïde net produit un **clic** désagréable. On applique donc une
**enveloppe** : le volume monte au début et redescend à la fin.

```
   volume
    1 │    ╭──────────────╮
      │   ╱                ╲
    0 │__╱                  ╲__
      └──────────────────────▶ temps
        fondu              fondu
```

```python
        fade = max(1, sample_count // 10)
        if i < fade:
            envelope = i / fade
        elif i >= sample_count - fade:
            envelope = (sample_count - 1 - i) / fade
        else:
            envelope = 1.0
```

Un dixième de la durée de chaque côté suffit : le son est doux, sans perte notable.

## 4. `SoundManager` : le son, mais pas indispensable

```python
class SoundManager:
    def __init__(self, enabled=True):
        self.enabled = False
        self._sounds = {}
        if not enabled:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=settings.SOUND_SAMPLE_RATE, size=-16, channels=2)
            self._sounds = {
                "hit": self._make(settings.SOUND_HIT_FREQ),
                "wall": self._make(settings.SOUND_WALL_FREQ),
                "point": self._make(settings.SOUND_SCORE_FREQ),
                "win": self._make(settings.SOUND_WIN_FREQ, duration_ms=320),
            }
            self.enabled = True
        except Exception:
            # Le son est optionnel : sans carte son, on continue en silence.
            self.enabled = False
```

Trois choix de conception à retenir :

1. **`enabled=False` dès la construction** : tant que tout n'est pas prêt, on est
   silencieux. En cas d'erreur, l'objet reste utilisable.
2. **Un `try / except` large assumé** : la cause peut être une absence de carte son,
   un format indisponible, une machine sans périphérique… Peu importe : le jeu ne
   doit **jamais** planter à cause du son. Un commentaire explique ce choix.
3. **Des méthodes nommées** (`paddle_hit`, `wall_bounce`…) plutôt qu'un `play("hit")`
   disséminé : si on renomme un son, on ne touche qu'un endroit.

```python
    def play(self, name):
        if self.enabled and name in self._sounds:
            self._sounds[name].play()

    def paddle_hit(self):
        self.play("hit")
```

## 5. Brancher les sons

Dans `GameScene`, on profite des valeurs déjà renvoyées par la logique :

```python
        for _ in range(steps):
            self.ball.update(sub_dt)
            if self.ball.handle_walls():     # renvoie True si rebond
                self.app.sound.wall_bounce()
            if self._handle_paddles():       # renvoie True si touche
                break
            if self.ball.off_screen() is not None:
                break

    def _handle_paddles(self):
        """Renvoie True si une collision balle/raquette a été traitée."""
        if self._resolve_paddle(self.left_paddle, direction=1):
            self._after_paddle_hit()
            return True
        if self._resolve_paddle(self.right_paddle, direction=-1):
            self._after_paddle_hit()
            return True
        return False

    def _after_paddle_hit(self):
        self.app.sound.paddle_hit()
        if self.ai is not None:
            self.ai.randomize_offset()   # nouvelle visée pour le prochain échange

        winner = self.score.add_point(scorer)
        self.app.sound.point_scored()
        if winner is not None:
            self.app.sound.win()
```

> 💡 Voyez comme le fait d'avoir fait **renvoyer un booléen** à `handle_walls`
> (chapitre 04) et `_handle_paddles` (chapitre 05) paie maintenant : le son se
> branche là où la collision est déjà détectée (`_after_paddle_hit`), et le `break`
> sort proprement des sous-étapes. En profiter pour réarmer la visée de l'IA
> (`randomize_offset`) évite un second `if` ailleurs.

## 6. La pause

Un écran de pause a une particularité : il **ne remplace pas** la partie, il la
**recouvre**. On garde donc une référence vers la scène de jeu :

```python
class PauseScene(Scene):
    def __init__(self, app, game):
        super().__init__(app)
        self.game = game

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_PAUSE or event.key in settings.KEY_VALIDATE:
            self.app.set_scene(self.game)        # reprendre
        elif event.key in settings.KEY_MENU:
            self.app.switch_scene("menu")        # abandonner

    def draw(self, surface):
        self.game.draw(surface)                  # la partie, figée, en fond
        overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        overlay.set_alpha(190)
        overlay.fill(settings.OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))
        ...
```

Deux points essentiels :

- **`set_scene(self.game)`** : on **réactive** la partie telle quelle, avec son
  score et ses positions — c'est exactement pour cela que `set_scene` existe
  (chapitre 02). `switch_scene("game")` créerait une partie **neuve**.
- **Le jeu ne se met pas à jour** pendant la pause : `PauseScene.update` ne fait
  rien, donc la balle est bien figée. La partie ne bouge que parce que
  `PauseScene.draw` appelle `self.game.draw(surface)`.

Ajoutez à `settings.py` :

```python
KEY_PAUSE = (pygame.K_p, pygame.K_ESCAPE)
OVERLAY_COLOR = (18, 6, 46)     # voile sombre par-dessus le jeu (pause)
```

Et dans `GameScene` :

```python
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in settings.KEY_PAUSE:
            self.app.set_scene(PauseScene(self.app, self))
```

## À vous de jouer !

1. Ajoutez les constantes de son et `OVERLAY_COLOR` à `settings.py`.
2. Écrivez `generate_tone` et `SoundManager` (`pong/sound.py`).
3. Écrivez `tests/test_sound.py` :
   - `generate_tone` renvoie le bon **nombre d'octets** (2 canaux × 2 octets ×
     échantillons) ;
   - le début et la fin sont **atténués** (fondu), le milieu non ;
   - un `SoundManager(enabled=False)` ne joue rien et **ne plante pas**.
4. Créez `PauseScene` et branchez-la sur la touche `P`/`Échap`.
5. Créez le `SoundManager` dans `App` et appelez les bruitages aux bons endroits.

<details>
<summary>Un indice sur le calcul du nombre d'octets</summary>

```python
sample_count = int(sample_rate * duration_ms / 1000)
expected_bytes = sample_count * 2      # 2 canaux
expected_bytes *= 2                    # 2 octets par échantillon (16 bits)
```

</details>

## Corrigé

### `pong/sound.py`

```python
"""Sons générés en code (aucun fichier audio).

`generate_tone` produit un buffer d'onde sinusoïdale 16 bits stéréo exploitable
directement par pygame. `SoundManager` encapsule la lecture et se dégrade
proprement si le matériel audio n'est pas disponible (environnement sans carte
son, exécution en CI, etc.).
"""

import array
import math

import pygame

from . import settings


def generate_tone(frequency, duration_ms, sample_rate=settings.SOUND_SAMPLE_RATE,
                  volume=settings.SOUND_VOLUME):
    """Génère un buffer PCM 16 bits signé stéréo d'une sinusoïdale.

    Renvoie des octets prêts pour `pygame.mixer.Sound(buffer=...)`.
    """
    sample_count = int(sample_rate * duration_ms / 1000)
    amplitude = int(32767 * volume)
    # Fondu (fade) au début et à la fin : évite le « clic » d'une coupure nette.
    fade = max(1, sample_count // 10)
    samples = array.array("h")
    for i in range(sample_count):
        if i < fade:
            envelope = i / fade
        elif i >= sample_count - fade:
            envelope = (sample_count - 1 - i) / fade
        else:
            envelope = 1.0
        value = int(amplitude * envelope * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.append(value)  # canal gauche
        samples.append(value)  # canal droit
    return samples.tobytes()


class SoundManager:
    """Joue les bruitages du jeu, ou reste silencieux si l'audio est indisponible."""

    def __init__(self, enabled=True):
        self.enabled = False
        self._sounds = {}
        if not enabled:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=settings.SOUND_SAMPLE_RATE, size=-16, channels=2
                )
            self._sounds = {
                "hit": self._make(settings.SOUND_HIT_FREQ),
                "wall": self._make(settings.SOUND_WALL_FREQ),
                "point": self._make(settings.SOUND_SCORE_FREQ),
                "win": self._make(settings.SOUND_WIN_FREQ, duration_ms=320),
            }
            self.enabled = True
        except Exception:
            # Le son est optionnel : quelle que soit la cause (pas de carte son,
            # format indisponible...), on continue en silence plutôt que planter.
            self.enabled = False

    @staticmethod
    def _make(frequency, duration_ms=settings.SOUND_DURATION_MS):
        return pygame.mixer.Sound(buffer=generate_tone(frequency, duration_ms))

    def play(self, name):
        if self.enabled and name in self._sounds:
            self._sounds[name].play()

    def paddle_hit(self):
        self.play("hit")

    def wall_bounce(self):
        self.play("wall")

    def point_scored(self):
        self.play("point")

    def win(self):
        self.play("win")
```

### `tests/test_sound.py` (extraits)

```python
"""Tests de la génération de sons et de la robustesse du gestionnaire audio."""

import struct

from pong import settings
from pong.sound import SoundManager, generate_tone


def test_tone_length_matches_duration():
    data = generate_tone(440, 90)
    expected_samples = int(settings.SOUND_SAMPLE_RATE * 90 / 1000)
    # 2 octets par échantillon, 2 canaux (stéréo)
    assert len(data) == expected_samples * 4


def test_tone_fades_in_and_out():
    data = generate_tone(440, 90)
    values = struct.unpack("<" + "h" * (len(data) // 2), data)
    # Enveloppe : premier et dernier échantillons à zéro (pas de clic).
    assert values[0] == 0
    assert values[-1] == 0


def test_disabled_sound_manager_is_safe():
    sound = SoundManager(enabled=False)
    assert sound.enabled is False
    # Aucune exception ne doit être levée quand le son est désactivé.
    sound.paddle_hit()
    sound.wall_bounce()
    sound.point_scored()
    sound.win()
```

### `pong/scenes/pause.py`

```python
"""Écran de pause : fige la partie en cours et affiche un overlay."""

import pygame

from .. import settings
from .base import Scene


class PauseScene(Scene):
    """Overlay affiché par-dessus la partie, sans la mettre à jour."""

    def __init__(self, app, game):
        super().__init__(app)
        self.game = game

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_PAUSE or event.key in settings.KEY_VALIDATE:
            self.app.set_scene(self.game)
        elif event.key in settings.KEY_MENU:
            self.app.switch_scene("menu")

    def draw(self, surface):
        self.game.draw(surface)  # partie figée en arrière-plan

        overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        overlay.set_alpha(190)
        overlay.fill(settings.OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))

        center_x = settings.WINDOW_WIDTH // 2
        self.app.draw_text(surface, "PAUSE", self.app.font_large,
                           settings.NEON_CYAN, center=(center_x, 250))
        self.app.draw_text(surface, "P ou Entrée : reprendre", self.app.font_small,
                           settings.TEXT_COLOR, center=(center_x, 330))
        self.app.draw_text(surface, "Q : retour au menu", self.app.font_small,
                           settings.TEXT_DIM, center=(center_x, 365))
```

Faites une partie, appuyez sur `P` : le jeu se fige, et `P` (ou Entrée) reprend
exactement où vous en étiez — même score, mêmes positions.

> **Dans le projet de référence :** `pong/sound.py` est identique. La pause
> utilisera `pong/ui.py` pour centrer ses trois lignes sur les métriques de police
> (chapitre 11) et un halo néon (chapitre 12).

## En résumé

- Un son numérique est une suite d'**échantillons** ; une note pure est une
  **sinusoïde**.
- pygame attend un **buffer PCM** 16 bits ; `array("h")` le construit.
- Un **fondu** aux extrémités supprime le « clic ».
- Un module de son doit **dégrader proprement** : le jeu ne plante pas sans audio.
- La pause **recouvre** la partie ; `set_scene` la reprend sans la recréer.

## Étape suivante

→ [10 — La fin de partie](10-la-fin-de-partie.md)
