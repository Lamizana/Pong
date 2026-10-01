"""Tests de la génération de sons et de la robustesse du gestionnaire audio."""

import struct

from pong import settings
from pong.sound import SoundManager, generate_tone


def test_tone_length_matches_duration():
    data = generate_tone(440, 90)
    expected_samples = int(settings.SOUND_SAMPLE_RATE * 90 / 1000)
    # 2 octets par échantillon, 2 canaux (stéréo)
    assert len(data) == expected_samples * 4


def test_tone_amplitude_within_range():
    data = generate_tone(440, 90, volume=0.5)
    values = struct.unpack("<" + "h" * (len(data) // 2), data)
    ceiling = int(32767 * 0.5)
    assert max(values) <= ceiling + 1
    assert min(values) >= -ceiling - 1
    assert max(values) > 0


def test_tone_is_not_silent():
    data = generate_tone(440, 90)
    assert any(byte != 0 for byte in data)


def test_disabled_sound_manager_is_safe():
    sound = SoundManager(enabled=False)
    assert sound.enabled is False
    # Aucune exception ne doit être levée quand le son est désactivé.
    sound.paddle_hit()
    sound.wall_bounce()
    sound.point_scored()
    sound.win()
