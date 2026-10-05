# 11 — Le thème par images

## Objectifs

À la fin de ce chapitre, vous saurez :

- comprendre la **chaîne des assets** : image source → PNG préparé → écran ;
- ce qu'est un **détourage** (« chroma-key ») et pourquoi on le fait **hors ligne** ;
- charger une image avec pygame et choisir entre `convert()` et `convert_alpha()` ;
- centraliser le chargement dans un **`AssetStore`** ;
- remplacer des formes dessinées par des **sprites**, sans toucher à la logique ;
- habiller le menu d'un **panneau** et d'un **titre** venus d'images.

**Fichiers du projet :** `scripts/prepare_assets.py`, `pong/resources.py`, `pong/ui.py`, `pong/scenes/*.py`
**Test du projet :** `tests/test_assets.py`, `tests/test_prepare_assets.py`

## 1. Du dessin au sprite

Jusqu'ici, nos raquettes étaient des `pygame.draw.rect`. C'est efficace, mais
austère. Pour habiller le jeu, on va charger des **images** (des « sprites »).

La question à se poser tout de suite : **où** charger ces images ?

- ❌ Les charger à chaque image (60 fois par seconde) : lecture disque permanente,
  jeu lent.
- ❌ Les charger dans chaque scène : on relit les mêmes fichiers, et on duplique le
  code.
- ✅ Les charger **une fois**, au démarrage, dans un objet partagé.

Ce sera le rôle de l'**`AssetStore`**.

## 2. La chaîne des assets

Un sprite de jeu a rarement la forme finale souhaitée. Nos images sources viennent
d'un générateur d'images : elles sont en JPEG, sur **fond vert**, en très haute
résolution.

```
  images/raquette_gauche.jpeg         (source, 2816 × 1536, fond vert)
              │
              │  scripts/prepare_assets.py   ← exécuté UNE fois, hors ligne
              ▼
  pong/assets/paddle_left.png         (35 × 80, fond transparent)
              │
              │  AssetStore                   ← exécuté au démarrage du jeu
              ▼
         pygame.Surface                 (prêt à blitter)
```

Trois étapes, trois responsabilités :

| Étape | Quand | Rôle |
|-------|-------|------|
| `prepare_assets.py` | à la main, une fois | détourer, recadrer, redimensionner |
| `pong/assets/*.png` | — | le résultat, **embarqué** avec le jeu |
| `AssetStore` | au lancement | charger en mémoire, une seule fois |

> 💡 **Pourquoi préparer hors ligne ?** Parce que le détourage est coûteux (des
> millions de pixels) et surtout parce que le résultat doit être **identique à
> chaque lancement**. Le joueur, lui, ne paie rien : il charge juste des PNG.

## 3. Le détourage (« chroma-key »)

Le fond vert n'est pas décoratif : c'est un **fond à supprimer**. On rend
transparent tout pixel où le vert domine nettement.

```python
GREEN_THRESHOLD = 40

def is_green_background(r, g, b):
    """Vrai si le pixel (r, g, b) appartient au fond vert à détourer."""
    return g > r + GREEN_THRESHOLD and g > b + GREEN_THRESHOLD
```

En pratique, on le fait d'un coup sur toute l'image avec des opérations PIL
(librairie **Pillow**), bien plus rapides qu'une boucle Python :

```python
    r, g, b = image.convert("RGB").split()
    green = ImageChops.multiply(
        ImageChops.subtract(g, r).point(lambda v: 255 if v > GREEN_THRESHOLD else 0),
        ImageChops.subtract(g, b).point(lambda v: 255 if v > GREEN_THRESHOLD else 0),
    )
    keep = ImageChops.invert(green)
    out = image.convert("RGBA")
    out.putalpha(keep)
```

Quelques compléments indispensables :

- **érosion** (`MinFilter`) : retire le liseré vert d'un pixel sur le contour ;
- **`clean_alpha`** : force à zéro les opacités minuscules (1-2 %) laissées par le
  redimensionnement, pour des coins nets ;
- **`despill`** : sur les seuls pixels semi-transparents, ramène le vert à
  `max(rouge, bleu)` — supprime la teinte verte résiduelle.

```python
def despill_green(image):
    r, g, b, a = image.split()
    semi = a.point(lambda v: 255 if 0 < v < 255 else 0)
    vert_limite = ImageChops.darker(g, ImageChops.lighter(r, b))
    return Image.merge("RGBA", (r, Image.composite(vert_limite, g, semi), b, a))
```

> ⚠️ **Le fond n'est pas toujours du même vert !** Notre image de titre utilise un
> vert **sombre**, que la règle ci-dessus ne détecte pas (le bleu y est trop proche
> du vert). D'où une seconde règle, fondée sur la **dominante verte + une faible
> luminance** (`remove_dark_green_background`). Morale : un détourage se vérifie
> **sur les vraies images**, jamais « en principe ».

## 4. Charger une image avec pygame

```python
import pygame

pygame.image.load(str(chemin))
```

Deux conversions sont possibles, et le choix n'est **pas** anodin :

| Méthode | Quand | Résultat |
|---------|-------|----------|
| `.convert()` | image **opaque** (un fond) | format d'affichage, plus rapide à dessiner |
| `.convert_alpha()` | image avec **transparence** (un sprite) | conserve le canal alpha |

> 💡 Convertir une image au format de l'écran accélère énormément le dessin. On le
> fait **une fois**, au chargement — jamais par image.

## 5. `asset_path` : des erreurs claires

Si une image manque, on veut le savoir **tout de suite**, et savoir **laquelle** :

```python
ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def asset_path(name):
    """Chemin absolu d'un asset, avec une erreur claire s'il est absent."""
    path = ASSETS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Asset introuvable : {path}")
    return path
```

Pourquoi `Path(__file__).resolve().parent` et pas un chemin relatif ? Parce que
l'exécutable packagé (chapitre 12) n'a pas le même dossier courant que le projet :
le chemin **relatif à ce fichier** est le seul fiable dans les deux cas.

## 6. L'`AssetStore`

```python
class AssetStore:
    """Images du jeu, chargées une fois puis réutilisées par les scènes."""

    def __init__(self):
        self.background = self._load_opaque(settings.ASSET_BACKGROUND)
        ...

    @staticmethod
    def _load_opaque(name):
        return pygame.image.load(str(asset_path(name))).convert()

    @staticmethod
    def _load_sprite(name):
        return pygame.image.load(str(asset_path(name))).convert_alpha()
```

Et dans `App.__init__` :

```python
        self.assets = AssetStore()
```

Toutes les scènes y accèdent par `self.app.assets.raquette`, etc.

## 7. Le sprite n'est que l'habillage

Point crucial : passer aux images **ne change pas la logique**. Le rectangle de
collision reste `paddle.rect` (calculé), et le sprite est simplement **blitté
dessus**.

```python
    def _draw_paddles(self, surface):
        """Blitte les sprites, zone de frappe alignée sur le bord intérieur."""
        left = self.app.assets.paddle_left
        right = self.app.assets.paddle_right
        surface.blit(left, (self.left_paddle.rect.right - left.get_width(),
                            self.left_paddle.center_y - left.get_height() // 2))
        surface.blit(right, (self.right_paddle.rect.left,
                             self.right_paddle.center_y - right.get_height() // 2))
```

> 💡 **La règle d'or :** la physique ne dépend jamais d'une taille de sprite. Ici,
> le sprite **déborde vers l'extérieur** du rectangle de collision, dont le bord
> intérieur marque la zone de frappe. Si vous régénérez l'image avec une autre
> largeur, le jeu reste correct — au pire, l'alignement visuel bouge d'un pixel.

Et la balle gagne même une petite animation : elle **tourne sur elle-même**,
proportionnellement à sa vitesse.

```python
    def _spin_ball(self, dt):
        """Fait rouler la balle sur elle-même, proportionnellement à sa vitesse."""
        spin = math.degrees(self.ball.vx / max(1.0, self.ball.radius))
        self.ball_angle = (self.ball_angle + spin * dt * settings.BALL_SPIN_FACTOR) % 360
```

## 8. Le panneau et le titre du menu

Last but not least : habiller les menus. L'image `menu_frame.png` est un panneau
avec un bord néon ; on la **réduit** pour qu'elle tienne dans le rectangle lumineux
du décor, puis on y dessine les choix.

```python
def fit_menu_frame(frame):
    """Réduit le cadre du menu pour qu'il tienne dans le rectangle bleu néon."""
    width = settings.FIELD_WIDTH - 40
    height = max(1, round(frame.get_height() * width / frame.get_width()))
    return pygame.transform.smoothscale(frame, (width, height))


def panel_rect(frame):
    """Rectangle du panneau : centré sur le terrain du décor."""
    return frame.get_rect(center=(
        (settings.FIELD_LEFT + settings.FIELD_RIGHT) // 2,
        (settings.FIELD_TOP + settings.FIELD_BOTTOM) // 2))
```

On regroupe ces helpers d'écran dans `pong/ui.py`, aux côtés de `navigation_index` :
**aucune scène n'a besoin de connaître la taille du panneau** pour l'afficher.

Le titre `PONG` devient lui aussi une image (`title.png`), blittée en haut du
panneau. Le texte passe en **clair** (le panneau est sombre) : ce sont les
constantes `TEXT_COLOR` / `TEXT_DIM` de `settings.py`.

> 💡 **Un détail qui compte :** les libellés lisibles sur un panneau **cyan** doivent
> être sombres ; sur un panneau **sombre**, ils doivent être clairs. Notre thème a
> changé de panneau en cours de route, et c'est une constante qui l'a absorbé —
> jamais une valeur codée en dur au fond d'une scène.

## À vous de jouer !

1. Ajoutez **Pillow** à vos dépendances de développement et écrivez
   `scripts/prepare_assets.py` (détourage, recadrage, redimensionnement).
2. Produisez (ou récupérez) les PNG dans `pong/assets/`.
3. Écrivez `pong/resources.py` : `ASSETS_DIR`, `asset_path`, `AssetStore`.
4. Branchez `AssetStore` dans `App` et remplacez les `pygame.draw.rect` / `draw.circle`
   par des `surface.blit` dans `GameScene`.
5. Ajoutez `fit_menu_frame`, `panel_rect` à `pong/ui.py` et habillez `MenuScene`.
6. Écrivez les tests :
   - chaque asset attendu existe **et** a une taille plausible ;
   - les quatre coins des sprites sont **transparents** ;
   - un asset manquant lève `FileNotFoundError` **en nommant le fichier** ;
   - les fonds ne sont **pas déformés** (ratio conservé).

<details>
<summary>Un indice sur la police de l'énoncé</summary>

```python
import pytest

with pytest.raises(FileNotFoundError, match="introuvable"):
    asset_path("fichier-inexistant.png")
```

</details>

## Corrigé

### `scripts/prepare_assets.py` (extraits)

```python
"""Prétraitement des images sources vers les assets du jeu.

Détoure le fond vert des sprites (chroma-key), recadre, redimensionne et écrit
les PNG dans `pong/assets/`. À lancer une fois, hors ligne.

Usage : python scripts/prepare_assets.py
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images"
OUT = ROOT / "pong" / "assets"

GREEN_THRESHOLD = 40
BACKGROUND_SIZE = (900, 600)


def is_green_background(r, g, b):
    return g > r + GREEN_THRESHOLD and g > b + GREEN_THRESHOLD


def remove_green_background(image, erode=3):
    """Renvoie une copie RGBA de `image` avec le fond vert rendu transparent."""
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


def build_background(source, dest):
    """Fond plein écran : scale-cover 900×600 (pas de déformation)."""
    image = ImageOps.fit(Image.open(SRC / source).convert("RGB"), BACKGROUND_SIZE,
                         method=Image.LANCZOS, centering=(0.5, 0.5))
    image.save(dest)


def build_sprite(source, dest, *, height=None, width=None, max_size=None):
    """Sprite transparent : détourage + recadrage + redimensionnement."""
    ...
```

> 💡 `ImageOps.fit` fait un « scale-cover » : l'image garde **ses proportions** et
> remplit tout le cadre, quitte à rogner. Un `resize` direct étirerait le décor.

### `pong/resources.py`

```python
"""Chargement des assets (images et police) du thème.

Le chemin est résolu via `__file__`, ce qui fonctionne en développement comme
dans l'exécutable PyInstaller (onefile), où les données sont extraites à côté du
module.
"""

from pathlib import Path

import pygame

from . import settings

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def asset_path(name):
    """Chemin absolu d'un asset, avec une erreur claire s'il est absent."""
    path = ASSETS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Asset introuvable : {path}")
    return path


class AssetStore:
    """Images du jeu, chargées une fois puis réutilisées par les scènes."""

    def __init__(self):
        self.background = self._load_opaque(settings.ASSET_BACKGROUND)
        self.menu_background = self._load_opaque(settings.ASSET_MENU)
        self.menu_frame = self._load_sprite(settings.ASSET_MENU_FRAME)
        self.title = self._load_sprite(settings.ASSET_TITLE)
        self.score_screen = self._load_sprite(settings.ASSET_SCORE_SCREEN)
        self.paddle_left = self._load_sprite(settings.ASSET_PADDLE_LEFT)
        self.paddle_right = self._load_sprite(settings.ASSET_PADDLE_RIGHT)
        self.ball = self._load_sprite(settings.ASSET_BALL)

    @staticmethod
    def _load_opaque(name):
        """Fond sans transparence, converti au format d'affichage."""
        return pygame.image.load(str(asset_path(name))).convert()

    @staticmethod
    def _load_sprite(name):
        """Sprite à transparence, converti au format d'affichage."""
        return pygame.image.load(str(asset_path(name))).convert_alpha()
```

### `settings.py` — les noms d'assets

```python
# --- Assets (images du thème, générées par scripts/prepare_assets.py) ---
ASSET_BACKGROUND = "background.png"
ASSET_MENU = "menu.png"
ASSET_MENU_FRAME = "menu_frame.png"
ASSET_TITLE = "title.png"
ASSET_SCORE_SCREEN = "score_screen.png"
ASSET_PADDLE_LEFT = "paddle_left.png"
ASSET_PADDLE_RIGHT = "paddle_right.png"
ASSET_BALL = "ball.png"
```

### `tests/test_assets.py` (extraits)

```python
"""Tests du chargeur d'assets (chargement, tailles, transparence)."""

import pygame
import pytest

from pong import settings
from pong.resources import AssetStore, asset_path


def test_asset_store_loads_expected_sizes():
    pygame.display.set_mode((1, 1))
    store = AssetStore()

    assert store.background.get_size() == (900, 600)
    assert store.paddle_left.get_height() == settings.PADDLE_HEIGHT


def test_sprites_have_transparent_corners():
    pygame.display.set_mode((1, 1))
    store = AssetStore()

    for sprite in (store.paddle_left, store.paddle_right, store.ball):
        width, height = sprite.get_size()
        for corner in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)):
            assert sprite.get_at(corner).a == 0


def test_missing_asset_raises_a_clear_error():
    with pytest.raises(FileNotFoundError, match="introuvable"):
        asset_path("fichier-inexistant.png")
```

> **Dans le projet de référence :** c'est exactement cette architecture. Le
> `score_screen.png` y est extrait du panneau de menu, et les positions de score
> sont dérivées de la largeur du panneau — jamais codées en dur.

## En résumé

- La chaîne est **source → script de préparation → PNG → chargement**.
- On prépare les images **hors ligne** ; le jeu, lui, ne fait que charger.
- Un **détourage** se vérifie sur les vraies images (fonds de verts différents !).
- `.convert()` pour l'opaque, `.convert_alpha()` pour la transparence.
- Un **`AssetStore`** charge tout une fois, et le partage entre les scènes.
- Un sprite est un **habillage** : la logique (collision, bornes) ne dépend jamais
  de sa taille.

## Étape suivante

→ [12 — Le polish et le déploiement](12-polish-et-deploiement.md)
