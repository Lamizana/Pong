"""Tests du prétraitement des images (détourage chroma-key)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image  # noqa: E402

from scripts.prepare_assets import (  # noqa: E402
    clean_alpha,
    crop_region,
    crop_to_content,
    despill_green,
    fit_width,
    is_green_background,
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


def test_despill_green_clears_fringe_only():
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (100, 200, 120, 128))   # bord verdâtre → vert ramené
    image.putpixel((1, 0), (100, 200, 120, 255))   # intérieur opaque → intact

    out = despill_green(image)

    assert out.getpixel((0, 0))[:3] == (100, 120, 120)
    assert out.getpixel((1, 0))[:3] == (100, 200, 120)


def test_build_background_keeps_aspect_ratio(tmp_path, monkeypatch):
    """Le fond est recadré (scale-cover), jamais étiré."""
    import scripts.prepare_assets as prepare

    monkeypatch.setattr(prepare, "SRC", tmp_path)
    source = Image.new("RGB", (300, 100), (0, 0, 0))
    for x in range(100, 110):
        for y in range(45, 55):
            source.putpixel((x, y), (255, 0, 0))
    source.save(tmp_path / "source.png")

    prepare.build_background("source.png", tmp_path / "out.png")

    out = Image.open(tmp_path / "out.png").convert("RGB")
    assert out.size == (900, 600)
    px = out.load()
    xs, ys = [], []
    for y in range(out.height):
        for x in range(out.width):
            r, g, _ = px[x, y]
            if r > 200 and g < 60:
                xs.append(x)
                ys.append(y)
    assert xs, "le motif de référence est introuvable"
    largeur = max(xs) - min(xs) + 1
    hauteur = max(ys) - min(ys) + 1
    # Un carré source doit rester carré ; un étirement donnerait ~30×60.
    assert abs(largeur - hauteur) <= 4


def test_build_start_video_fits_the_whole_video(tmp_path, monkeypatch):
    """La vidéo 16:9 tient entière dans les frames : bandes noires, pas de rognage."""
    import shutil
    import subprocess

    import pytest
    import scripts.prepare_assets as prepare

    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg absent")

    # Clip de test 16:9 (640×360) au motif clair : le contenu est maîtrisé.
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", "testsrc2=size=640x360:rate=10:duration=0.5",
         str(tmp_path / "video.mp4")],
        check=True,
    )
    monkeypatch.setattr(prepare, "SRC", tmp_path)

    count = prepare.build_start_video("video.mp4", tmp_path / "out")

    assert count >= 1
    frame = Image.open(
        tmp_path / "out" / prepare.START_VIDEO_DIR / "frame_001.jpg"
    ).convert("RGB")
    assert frame.size == (900, 600)

    px = frame.load()
    # 16:9 dans 3:2 → 900×506 : bandes noires de 47 px en haut et en bas.
    assert all(max(px[x, y]) < 16
               for x in range(0, 900, 10) for y in (2, 8, 592, 598))
    # Le motif de la vidéo reste visible au centre (un recadrage remplirait tout).
    assert any(max(px[x, y]) > 40
               for x in range(0, 900, 10) for y in (250, 300, 350))
