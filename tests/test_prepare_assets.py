"""Tests du prétraitement des images (détourage chroma-key)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image  # noqa: E402

from scripts.prepare_assets import (  # noqa: E402
    clean_alpha,
    crop_region,
    crop_to_content,
    fit_width,
    is_green_background,
    remove_dark_green_background,
    remove_green_background,
)


def test_green_background_detected():
    assert is_green_background(16, 172, 37)   # fond balle
    assert is_green_background(60, 165, 77)   # fond raquette


def test_foreground_kept():
    for r, g, b in [(129, 129, 131),   # gris
                    (196, 130, 70),    # cuivre
                    (0, 229, 255),     # cyan
                    (255, 45, 149),    # rose
                    (225, 255, 253)]:  # cœur balle
        assert not is_green_background(r, g, b)


def test_remove_green_background_drops_green_keeps_foreground():
    image = Image.new("RGB", (3, 1))
    image.putpixel((0, 0), (16, 172, 37))    # fond vert → transparent
    image.putpixel((1, 0), (129, 129, 131))  # gris → conservé
    image.putpixel((2, 0), (0, 229, 255))    # cyan → conservé

    out = remove_green_background(image, erode=1)

    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((1, 0))[3] == 255
    assert out.getpixel((2, 0))[3] == 255


def test_crop_to_content_ignores_border_noise():
    image = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    for x in range(8, 12):          # carré opaque au centre
        for y in range(8, 12):
            image.putpixel((x, y), (255, 255, 255, 255))
    for y in range(20):             # liseré parasite sur le bord gauche
        image.putpixel((0, y), (255, 255, 255, 255))

    out = crop_to_content(image, margin=2)

    assert out.size == (4, 4)


def test_clean_alpha_zeroes_faint_pixels():
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (255, 0, 0, 1))     # quasi transparent → 0
    image.putpixel((1, 0), (255, 0, 0, 200))   # opaque → conservé

    out = clean_alpha(image, threshold=16)

    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((1, 0))[3] == 200


def test_fit_width_preserves_ratio():
    image = Image.new("RGBA", (200, 100), (255, 0, 0, 255))

    out = fit_width(image, 400)

    assert out.size == (400, 200)


def test_crop_region_uses_relative_box():
    image = Image.new("RGBA", (100, 50), (255, 0, 0, 255))

    out = crop_region(image, (0.2, 0.4, 0.8, 0.6))

    assert out.size == (60, 10)


def test_remove_dark_green_background_keys_dark_green():
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (2, 60, 45, 255))      # vert sombre → transparent
    image.putpixel((1, 0), (150, 255, 238, 255))  # lettre claire → conservée

    out = remove_dark_green_background(image)

    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((1, 0))[3] == 255
