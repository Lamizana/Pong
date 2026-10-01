# 09 — Les sons

Un jeu sans son paraît bien fade. Bonne nouvelle : pas besoin de télécharger des
fichiers audio. On va **générer** nos bruitages en Python, sous forme d'ondes
sinusoïdales.

## Le principe

Un son, c'est une variation de pression dans l'air. Numériquement, on la représente
par une suite de **nombreuses mesures** (les « échantillons ») prises des milliers de
fois par seconde. Pour un bip pur, chaque échantillon suit une **sinusoïde** :

```python
import array
import math

def generate_tone(frequency, duration_ms, sample_rate=44100, volume=0.4):
    sample_count = int(sample_rate * duration_ms / 1000)
    amplitude = int(32767 * volume)
    samples = array.array("h")          # entiers signés 16 bits
    for i in range(sample_count):
        value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.append(value)           # canal gauche
        samples.append(value)           # canal droit
    return samples.tobytes()
```

Quelques points clés :

- **`sample_rate`** = 44 100 Hz, le standard audio. Une note de 90 ms contient donc
  `44100 × 0.09 ≈ 3970` échantillons.
- **`array("h")`** crée un tableau d'entiers 16 bits signés (valeurs de -32768 à
  32767), le format attendu par pygame.
- On écrit **deux fois** chaque valeur, une pour le canal gauche, une pour le droit :
  le son est **stéréo**.
- `frequency` est la hauteur du son (440 Hz = le « la ») ; `volume` règle l'amplitude.

## Transformer ces octets en son pygame

pygame sait lire directement un tampon d'octets :

```python
import pygame

if not pygame.mixer.get_init():
    pygame.mixer.init(frequency=44100, size=-16, channels=2)

sound = pygame.mixer.Sound(buffer=generate_tone(440, 90))
```

Le paramètre `size=-16` signifie « 16 bits signés », et `channels=2` « stéréo ».
Ces réglages **doivent** correspondre à ce que produit `generate_tone`, sinon le son
sera déformé.

## Un gestionnaire robuste

Tout le monde n'a pas de carte son — un serveur, une machine virtuelle, ou
l'intégration continue, par exemple. Le `SoundManager` essaie d'initialiser l'audio
et, en cas d'échec, se met simplement en **silence** au lieu de planter :

```python
class SoundManager:
    def __init__(self, enabled=True):
        self.enabled = False
        self._sounds = {}
        if not enabled:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2)
            self._sounds = {
                "hit": self._make(settings.SOUND_HIT_FREQ),
                "wall": self._make(settings.SOUND_WALL_FREQ),
                "point": self._make(settings.SOUND_SCORE_FREQ),
                "win": self._make(settings.SOUND_WIN_FREQ, duration_ms=320),
            }
            self.enabled = True
        except pygame.error:
            self.enabled = False      # pas de matériel audio : on continue en silence
```

Chaque événement du jeu appelle une petite méthode, qui ne fait rien si le son est
indisponible :

```python
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

## Où déclencher les sons ?

Dans la scène de jeu, au moment exact où se produit l'événement :

| Événement | Appel |
|-----------|-------|
| La balle touche une raquette | `self.app.sound.paddle_hit()` |
| La balle touche un mur | `self.app.sound.wall_bounce()` |
| Un point est marqué | `self.app.sound.point_scored()` |
| La partie est gagnée | `self.app.sound.win()` |

Par exemple, dans `_handle_paddles` :

```python
def _after_paddle_hit(self):
    self.app.sound.paddle_hit()
    if self.ai is not None:
        self.ai.randomize_offset()
```

## Tester sans son

On teste la **génération** (pure, sans matériel) et la **robustesse** du gestionnaire
désactivé :

```python
def test_tone_length_matches_duration():
    data = generate_tone(440, 90)
    expected_samples = int(44100 * 90 / 1000)
    assert len(data) == expected_samples * 4   # 2 octets × 2 canaux


def test_disabled_sound_manager_is_safe():
    sound = SoundManager(enabled=False)
    assert sound.enabled is False
    sound.paddle_hit()          # ne doit lever aucune exception
```

## Étape suivante

→ [10 — La pause](10-la-pause.md)
