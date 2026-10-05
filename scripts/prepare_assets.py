"""Prétraitement des images sources vers les assets du jeu.

Détoure le fond vert des sprites (chroma-key), recadre, redimensionne et
écrit les PNG dans `pong/assets/`. À lancer une fois, hors ligne, après
avoir déposé les images dans `images/`.

Usage : python scripts/prepare_assets.py
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps

# Racine du projet = dossier parent de `scripts/`.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images"
OUT = ROOT / "pong" / "assets"

# Seuil du chroma-key : un pixel est « fond vert » si le canal vert dépasse
# nettement le rouge ET le bleu (le fond échantillonné est ≈ (16,172,37) pour
# la balle et ≈ (60,165,76) pour les raquettes).
GREEN_THRESHOLD = 40

# Taille finale des fonds (fenêtre du jeu).
BACKGROUND_SIZE = (900, 600)

# Panneau de score : région (relative) de l'image de menu 01, et hauteur cible.
# La région couvre le panneau entier, sans le bord néon qui l'entoure.
SCORE_SCREEN_BOX = (0.063, 0.130, 0.936, 0.870)
SCORE_SCREEN_HEIGHT = 72


def is_green_background(r, g, b):
    """Vrai si le pixel (r, g, b) appartient au fond vert à détourer."""
    return g > r + GREEN_THRESHOLD and g > b + GREEN_THRESHOLD


def remove_green_background(image, erode=3):
    """Renvoie une copie RGBA de `image` avec le fond vert rendu transparent.

    `erode` : taille (impaire) de l'érosion du masque alpha, qui retire le
    liseré vert sur le contour. 1 désactive l'érosion.
    """
    r, g, b = image.convert("RGB").split()
    green = ImageChops.multiply(
        ImageChops.subtract(g, r).point(lambda v: 255 if v > GREEN_THRESHOLD else 0),
        ImageChops.subtract(g, b).point(lambda v: 255 if v > GREEN_THRESHOLD else 0),
    )
    keep = ImageChops.invert(green)
    if erode > 1:
        keep = keep.filter(ImageFilter.MinFilter(erode))

    out = image.convert("RGBA")
    out.putalpha(keep)
    return out


def crop_to_content(image, margin=8):
    """Recadre l'image sur la zone non transparente.

    `margin` : nombre de pixels ignorés sur chaque bord. Les images générées
    comportent parfois un fin liseré clair (1-3 px) sur un bord, qui fausserait
    le calcul de la boîte englobante et produirait un sprite trop large.
    """
    alpha = image.getchannel("A").copy()
    width, height = alpha.size
    margin = min(margin, width // 2, height // 2)
    for d in range(margin):
        for x in range(width):
            alpha.putpixel((x, d), 0)
            alpha.putpixel((x, height - 1 - d), 0)
        for y in range(height):
            alpha.putpixel((d, y), 0)
            alpha.putpixel((width - 1 - d, y), 0)

    bbox = alpha.getbbox()
    return image.crop(bbox) if bbox else image


def crop_region(image, box):
    """Découpe une région de l'image ; `box` en coordonnées relatives (0..1)."""
    width, height = image.size
    return image.crop((int(box[0] * width), int(box[1] * height),
                       int(box[2] * width), int(box[3] * height)))


def fit_height(image, height):
    """Redimensionne en conservant le ratio pour obtenir `height` de haut."""
    width, current = image.size
    new_width = max(1, round(width * height / current))
    return image.resize((new_width, height), Image.LANCZOS)


def fit_width(image, width):
    """Redimensionne en conservant le ratio pour obtenir `width` de large."""
    current, height = image.size
    new_height = max(1, round(height * width / current))
    return image.resize((width, new_height), Image.LANCZOS)


def fit_max(image, size):
    """Redimensionne pour que la plus grande dimension fasse `size`."""
    width, height = image.size
    scale = size / max(width, height)
    return image.resize((max(1, round(width * scale)), max(1, round(height * scale))),
                        Image.LANCZOS)


def clean_alpha(image, threshold=16):
    """Met à zéro les valeurs d'alpha quasi nulles.

    Le redimensionnement LANCZOS laisse des pixels à très faible opacité
    (alpha 1-2) sur les bords ; on les force à 0 pour des coins nets.
    """
    r, g, b, a = image.split()
    a = a.point(lambda v: 0 if v < threshold else v)
    return Image.merge("RGBA", (r, g, b, a))


def _load(name):
    path = SRC / name
    if not path.exists():
        raise FileNotFoundError(f"Image source introuvable : {path}")
    return Image.open(path)


def build_background(source, dest):
    """Fond plein écran : scale-cover 900×600 (pas de déformation)."""
    image = ImageOps.fit(_load(source).convert("RGB"), BACKGROUND_SIZE,
                         method=Image.LANCZOS, centering=(0.5, 0.5))
    image.save(dest)


def build_sprite(source, dest, *, height=None, width=None, max_size=None):
    """Sprite transparent : détourage + recadrage + redimensionnement."""
    image = crop_to_content(remove_green_background(_load(source)))
    if height is not None:
        image = fit_height(image, height)
    elif width is not None:
        image = fit_width(image, width)
    elif max_size is not None:
        image = fit_max(image, max_size)
    image = clean_alpha(image)
    image.save(dest)


def build_region(source, dest, box, *, height=None, width=None):
    """Extrait une région d'une image puis la redimensionne (PNG)."""
    image = crop_region(_load(source).convert("RGBA"), box)
    if height is not None:
        image = fit_height(image, height)
    elif width is not None:
        image = fit_width(image, width)
    image.save(dest)


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    build_background("fond_partie.jpeg", OUT / "background.png")
    build_background("fond_accueil.jpeg", OUT / "menu.png")
    build_sprite("raquette_gauche.jpeg", OUT / "paddle_left.png", height=80)
    build_sprite("raquette_droite.jpeg", OUT / "paddle_right.png", height=80)
    build_sprite("balle.jpeg", OUT / "ball.png", max_size=20)
    build_sprite("rectangle_menu_01.jpeg", OUT / "menu_frame.png", width=880)
    build_region("rectangle_menu_01.jpeg", OUT / "score_screen.png",
                 SCORE_SCREEN_BOX, height=SCORE_SCREEN_HEIGHT)

    for name in ("background", "menu", "paddle_left", "paddle_right", "ball",
                 "menu_frame", "score_screen"):
        path = OUT / f"{name}.png"
        with Image.open(path) as im:
            print(f"  {path.relative_to(ROOT)}  {im.size}  {im.mode}")


if __name__ == "__main__":
    main()
