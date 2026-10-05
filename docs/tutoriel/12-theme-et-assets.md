# 12 — Le thème : des images et une police

Jusqu'ici, nous avons construit un Pong fonctionnel sur fond noir. Ce chapitre lui
donne une identité visuelle **cyberpunk** : décor illustré (ville néon, portail), cadre
de jeu lumineux, raquettes mécaniques, balle cybernétique, panneau de menu, titre, et
une **police** dédiée.

![Écran de jeu](../screenshots/game.png)

Point important : **aucune ligne de logique de jeu n'a changé**. Physique, IA, score
et scènes continuent de fonctionner exactement pareil. On ne touche qu'au **calque
d'affichage** — c'est tout l'intérêt d'avoir séparé le rendu de la logique.

## La chaîne des assets

Le thème ne dessine presque rien en code : il affiche des **images préparées à
l'avance**. Le trajet d'une image est toujours le même :

```
images/*.jpeg  →  scripts/prepare_assets.py  →  pong/assets/*.png  →  AssetStore
 (sources IA)      (détourage, recadrage)        (PNG finaux)         (au démarrage)
```

Les images sources vivent dans `images/` (hors dépôt : ce sont des fichiers lourds).
Les PNG produits, eux, sont **versionnés** et embarqués dans l'exécutable.

## Préparer les images : `scripts/prepare_assets.py`

Les images générées par IA ont un **fond vert uni** et des dimensions quelconques. Le
script fait le ménage, hors ligne, une fois pour toutes.

### Détourer le fond vert (chroma-key)

Même principe qu'un fond vert au cinéma : on rend transparent tout pixel où le vert
domine nettement le rouge **et** le bleu.

```python
def remove_green_background(image, erode=3):
    r, g, b = image.convert("RGB").split()
    green = ImageChops.multiply(
        ImageChops.subtract(g, r).point(lambda v: 255 if v > GREEN_THRESHOLD else 0),
        ImageChops.subtract(g, b).point(lambda v: 255 if v > GREEN_THRESHOLD else 0),
    )
    keep = ImageChops.invert(green)
    ...
```

Le titre, lui, utilise un vert **sombre** que cette règle laisse passer : une seconde
fonction (`remove_dark_green_background`) le repère par sa dominante verte **et** sa
faible luminance.

### Recadrer, redimensionner, nettoyer

- `crop_to_content` : recadre sur la zone non transparente, en ignorant un fin liseré
  de bord parfois présent sur les images générées ;
- `fit_width` / `fit_height` / `fit_max` : redimensionnent **en conservant le ratio** ;
- `clean_alpha` : force à zéro les opacités quasi nulles, pour des bords nets.

### Les fonds : « scale-cover », jamais étirés

Un fond ne doit pas être déformé : on **recadre** au lieu d'étirer.

```python
def build_background(source, dest):
    """Fond plein écran : scale-cover 900×600 (pas de déformation)."""
    image = ImageOps.fit(_load(source).convert("RGB"), BACKGROUND_SIZE,
                         method=Image.LANCZOS, centering=(0.5, 0.5))
    image.save(dest)
```

### Le résultat

`python scripts/prepare_assets.py` écrit dans `pong/assets/` :

| Fichier | Rôle |
|---|---|
| `background.png`, `menu.png` | Fonds de partie et d'accueil (900×600) |
| `paddle_left.png`, `paddle_right.png` | Raquettes |
| `ball.png` | Balle |
| `menu_frame.png` | Panneau commun des écrans (menu, options, fin) |
| `title.png` | Titre du menu |
| `score_screen.png` | Écran de score, au-dessus du terrain |

## Charger les assets : `pong/resources.py`

Deux points comptent ici : un **chemin** qui fonctionne partout, et une erreur
**lisible** quand un fichier manque.

```python
ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def asset_path(name):
    path = ASSETS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Asset introuvable : {path}")
    return path
```

Résoudre le chemin via `__file__` (plutôt qu'un chemin relatif au dossier courant)
fonctionne aussi dans l'exécutable PyInstaller en **fichier unique**, où les données
sont extraites à côté du module.

`AssetStore` charge une bonne fois chaque image, en distinguant les fonds
(`convert()`) des sprites à transparence (`convert_alpha()`) ; les scènes se contentent
ensuite de les blitter.

## La police Orbitron

Le thème utilise une police dédiée, **embarquée** elle aussi (licence libre OFL, voir
`pong/assets/OFL-Orbitron.txt`) :

```python
font_path = str(asset_path(settings.ASSET_FONT))
self.font_small = pygame.font.Font(font_path, 28)
self.font_medium = pygame.font.Font(font_path, 44)
self.font_large = pygame.font.Font(font_path, 72)
```

Comme la police est dans `pong/assets/`, le rendu reste **identique sous Linux et sous
Windows**, une fois l'exécutable construit.

## Les helpers d'affichage

Deux petits modules évitent de répéter le code dans chaque scène :

- `pong/neon.py` — `glow_text` : un texte entouré d'un halo diffus (plusieurs copies
  légèrement décalées, puis la version nette par-dessus) ;
- `pong/ui.py` — le panneau commun (`fit_menu_frame`, `panel_rect`), la navigation
  clavier (`navigation_index`) et le tracé des choix (`draw_choices`, `draw_hint`).

## Générer des aperçus

Le script `scripts/render_preview.py` dessine chaque écran hors ligne et enregistre des
PNG dans `docs/screenshots/` (sans ouvrir de fenêtre) :

```bash
python scripts/render_preview.py
```

C'est bien pratique pour illustrer le README ou vérifier un changement de style dans
la CI.

## Et le tutoriel dans tout ça ?

Les chapitres précédents construisent volontairement un thème **simple** (fond noir,
couleurs unies) : c'est la meilleure façon d'apprendre les mécanismes sans se perdre
dans l'esthétique. Ce chapitre-ci ajoute la couche de style **par-dessus**, sans rien
casser — exactement comme on procéderait sur un vrai projet.

---

[Retour au sommaire du tutoriel](README.md)
