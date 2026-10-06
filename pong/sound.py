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

    def play_music(self, path, loops=-1):
        """Joue une musique de fond en boucle (`loops=-1` = à l'infini)."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(loops)
        except Exception:
            # La musique est optionnelle : on continue sans elle.
            pass

    def stop_music(self):
        """Arrête la musique de fond, si une musique joue."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
