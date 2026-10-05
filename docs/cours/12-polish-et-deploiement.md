# 12 — Le polish et le déploiement

## Objectifs

À la fin de ce chapitre, vous saurez :

- ajouter un **halo néon** derrière un texte ;
- embarquer une **vraie police** (avec sa licence) et l'utiliser partout ;
- rendre les réglages **persistants** d'une session à l'autre ;
- afficher une **erreur lisible** même dans un exécutable sans console ;
- créer un **exécutable** Linux et Windows, et l'automatiser sur GitHub Actions.

**Fichiers du projet :** `pong/neon.py`, `pong/config.py`, `main.py`, `build.sh`, `build.ps1`, `.github/workflows/build.yml`, `pyproject.toml`
**Test du projet :** `tests/test_neon.py`, `tests/test_config.py`, `tests/test_main.py`, `tests/test_build_config.py`

## 1. Les halos néon

Un texte néon, c'est un texte net, doublé d'un **halo diffus**. La technique : on
dessine d'abord la même phrase plusieurs fois, légèrement **décalée** et dans une
couleur atténuée, puis le texte net par-dessus.

```python
def glow_text(surface, font, text, color, center, spread=3):
    """Texte néon : halo diffus puis texte net par-dessus."""
    dim = tuple(min(255, c // 2 + 50) for c in color[:3])
    base = font.render(text, True, dim)
    rect = base.get_rect(center=center)
    for dx in range(-spread, spread + 1, 2):
        for dy in range(-spread, spread + 1, 2):
            if dx or dy:
                surface.blit(base, (rect.x + dx, rect.y + dy))
    surface.blit(font.render(text, True, color), rect)
    return rect
```

- `dim` est une version **assombrie** de la couleur : c'est le halo.
- `range(-spread, spread + 1, 2)` place des copies tous les deux pixels dans un
  carré : un halo serré et régulier.
- Une seule fonction, utilisée par le menu, les options, la pause et la fin.

> ⚠️ **Un halo trop large fait « gras ».** `spread=1` donne un halo discret
> (4 copies), `spread=4` un halo très marqué (16 copies). À régler selon le goût.

## 2. Une vraie police

`SysFont(None, taille)` utilise la police du système : elle change d'une machine à
l'autre. Pour un rendu identique partout, on **embarque** une police.

1. Déposez le fichier dans `pong/assets/` (par exemple `Orbitron.ttf`).
2. **Ajoutez sa licence** à côté (`OFL-Orbitron.txt`) : la plupart des polices libres
   vous y obligent. C'est une question de respect… et de légalité.
3. Chargez-la dans `App` :

```python
        font_path = str(asset_path(settings.ASSET_FONT))
        self.font_small = pygame.font.Font(font_path, settings.FONT_SMALL_SIZE)
        self.font_medium = pygame.font.Font(font_path, settings.FONT_MEDIUM_SIZE)
        self.font_large = pygame.font.Font(font_path, settings.FONT_LARGE_SIZE)
```

Avec, dans `settings.py` :

```python
FONT_SMALL_SIZE = 28
FONT_MEDIUM_SIZE = 44
FONT_LARGE_SIZE = 72
```

> 💡 **Pourquoi les tailles sont-elles des constantes ?** Parce qu'une police large
> comme Orbitron ne se comporte pas comme une police étroite : on ajuste les tailles
> à un seul endroit, sans toucher aux scènes.

## 3. Des réglages qui survivent au redémarrage

Rappelez-vous le chapitre 08 : la difficulté et les points sont perdus à la
fermeture. Écrivons-les dans un fichier.

```python
DEFAULTS = {"level": "moyen", "points_to_win": settings.POINTS_TO_WIN}


def config_dir():
    """Dossier de configuration selon le système."""
    override = os.environ.get("PONG_CONFIG_DIR")
    if override:
        return Path(override)
    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        return Path(base) / "Pong" if base else Path.home() / "AppData" / "Roaming" / "Pong"
    base = os.environ.get("XDG_CONFIG_HOME")
    return Path(base) / "pong" if base else Path.home() / ".config" / "pong"
```

Trois principes de robustesse :

1. **Chaque système a ses conventions** (Windows aime `%APPDATA%`, Linux `XDG`).
2. **`PONG_CONFIG_DIR`** permet de tout rediriger — c'est ce qui rendra les tests
   hermétiques (aucun test n'écrit dans le dossier réel de l'utilisateur).
3. **Un fichier absent, illisible ou corrompu retombe sur les défauts.** Jamais de
   plantage à cause d'un réglage :

```python
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return config                    # valeurs par défaut
    ...
    if data.get("level") in settings.AI_LEVELS:      # on VALIDE les valeurs
        config["level"] = data["level"]
```

Et l'écriture est **best-effort** : si le disque est plein, on ne fait pas échouer
la partie pour autant (`save` renvoie `False`).

## 4. Ne jamais échouer en silence

Voilà un piège classique du déploiement : l'exécutable `--windowed` **n'a pas de
console**. Un asset manquant afficherait une trace d'erreur… nulle part. Le joueur
voit une fenêtre s'ouvrir, puis disparaître. Mystère.

La parade tient en dix lignes, dans `main.py` :

```python
def report_startup_error(message, log_dir=None):
    """Signale une erreur de démarrage là où l'utilisateur peut la voir."""
    print(message, file=sys.stderr)
    log_path = Path(log_dir) if log_dir else Path.cwd()
    log_path = log_path / LOG_NAME
    try:
        log_path.write_text(message + "\n", encoding="utf-8")
    except OSError:
        log_path = None
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, message, "Pong — démarrage impossible", 0x10)
        except Exception:
            pass
    return log_path


def main():
    try:
        app = App()
    except Exception as error:
        report_startup_error(f"Pong n'a pas pu démarrer :\n{error}")
        return 1
    app.run()
    return 0
```

Trois canaux, du plus discret au plus visible : **stderr** (console), un **fichier
journal** (`pong-error.log`, toujours écrit), et une **boîte de dialogue** sous
Windows. L'utilisateur a **toujours** moyen de comprendre ce qui s'est passé.

## 5. Créer un exécutable

PyInstaller rassemble Python, pygame, vos modules **et vos données** dans un seul
fichier exécutable.

```bash
pyinstaller --onefile --windowed --name Pong \
    --add-data "pong/assets:pong/assets" \
    main.py
```

- `--onefile` : un seul fichier à distribuer.
- `--windowed` : pas de console (d'où l'importance du point 4 !).
- `--add-data` : **embarque le dossier des assets**.

> 🔴 **L'erreur qui coûte une soirée.** Si vous oubliez `--add-data`, le jeu
> démarrera… puis plantera au chargement des images (`Asset introuvable : …`). Les
> données ne sont **pas** incluses automatiquement.
>
> ⚠️ Le séparateur dépend du système : **`:`** sous Linux/macOS, **`;`** sous
> Windows. D'où un petit script qui s'adapte :

```bash
# build.sh (Linux / macOS)
SEP=":"
pyinstaller --onefile --windowed --name Pong \
    --add-data "pong/assets${SEP}pong/assets" main.py
```

```powershell
# build.ps1 (Windows)
$SEP = ";"
pyinstaller --onefile --windowed --name Pong `
    --add-data "pong/assets$SEP pong/assets" main.py
```

Et pour ne pas reconstruire à la main, GitHub Actions le fait à chaque version :

```yaml
# .github/workflows/build.yml (extrait)
    - name: Compiler l'exécutable
      run: |
        if [ "$RUNNER_OS" = "Windows" ]; then SEP=";"; else SEP=":"; fi
        pyinstaller --onefile --windowed --name Pong \
          --add-data "pong/assets${SEP}pong/assets" main.py
```

## 6. Penser aux autres chemins d'installation

PyInstaller n'est pas le seul moyen de distribuer :

- **`pip install .`** : les images et la police doivent être déclarées comme
  **données de paquet**, sinon elles sont oubliées :

```toml
[tool.setuptools.package-data]
pong = ["assets/*"]

[tool.setuptools]
license-files = ["LICENSE", "pong/assets/OFL-Orbitron.txt"]
```

- **Depuis les sources** (`python main.py`) : tout fonctionne déjà, puisque le
  chemin est résolu par rapport au fichier.

## 7. La qualité, à la fin

Un dernier conseil : automatisez ce que vous vérifiez. Notre suite de tests attrape
déjà :

- la physique (rebonds, bornes, collisions),
- les règles (score, victoire),
- les parcours d'écran (menu, options, pause, fin),
- les **assets** (présents, tailles, transparence, coins nets),
- la **configuration** (défauts, validation, persistance),
- le **démarrage** (message d'erreur et code de sortie).

En tout, plus de **cent tests** qui tournent en quelques secondes :

```bash
pytest
```

## À vous de jouer !

1. Créez `pong/neon.py` avec `glow_text`, et utilisez-le pour les titres (menu,
   options, pause, fin).
2. Embarquez une police : téléchargez une police libre, placez-la dans
   `pong/assets/` **avec sa licence**, et chargez-la dans `App`.
3. Créez `pong/config.py` (dossier, `load`, `save`) et utilisez-le pour que les
   options soient conservées entre deux lancements.
4. Entourez `App()` d'un `try / except` dans `main.py`, avec journal et boîte de
   dialogue sous Windows.
5. Écrivez `build.sh` et `build.ps1`, puis **testez l'exécutable** : il doit
   démarrer **avec** ses images.
6. Écrivez les tests qui vous protègent : `glow_text` dessine bien, la config
   retombe sur les défauts si le fichier est corrompu, et le séparateur du build
   est le bon selon le système.

<details>
<summary>Un indice pour tester la configuration</summary>

Ne touchez **jamais** le vrai dossier de configuration pendant un test. Redirigez
`PONG_CONFIG_DIR` vers un dossier temporaire (via `monkeypatch.setenv`) et testez
`load(path)` / `save(config, path)` sur des fichiers maîtrisés.

</details>

## Corrigé

### `pong/neon.py`

```python
"""Effets néon du thème : halos derrière le texte."""


def glow_text(surface, font, text, color, center, spread=3):
    """Texte néon : halo diffus puis texte net par-dessus."""
    dim = tuple(min(255, c // 2 + 50) for c in color[:3])
    base = font.render(text, True, dim)
    rect = base.get_rect(center=center)
    for dx in range(-spread, spread + 1, 2):
        for dy in range(-spread, spread + 1, 2):
            if dx or dy:
                surface.blit(base, (rect.x + dx, rect.y + dy))
    surface.blit(font.render(text, True, color), rect)
    return rect
```

### `pong/config.py`

```python
"""Réglages persistants (difficulté, points pour gagner).

Enregistrés en JSON dans le dossier de configuration de l'utilisateur :

- `PONG_CONFIG_DIR` s'il est défini (pratique pour les tests) ;
- `%APPDATA%/Pong` sous Windows ;
- `$XDG_CONFIG_HOME/pong` ou `~/.config/pong` ailleurs.
"""

import json
import os
import sys
from pathlib import Path

from . import settings

DEFAULTS = {
    "level": "moyen",
    "points_to_win": settings.POINTS_TO_WIN,
}


def config_dir():
    """Dossier de configuration selon le système."""
    override = os.environ.get("PONG_CONFIG_DIR")
    if override:
        return Path(override)
    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        return Path(base) / "Pong" if base else Path.home() / "AppData" / "Roaming" / "Pong"
    base = os.environ.get("XDG_CONFIG_HOME")
    return Path(base) / "pong" if base else Path.home() / ".config" / "pong"


def config_path():
    """Chemin du fichier de configuration."""
    return config_dir() / "config.json"


def load(path=None):
    """Réglages enregistrés, complétés et validés par les valeurs par défaut."""
    path = Path(path) if path else config_path()
    config = dict(DEFAULTS)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return config
    if not isinstance(data, dict):
        return config
    if data.get("level") in settings.AI_LEVELS:
        config["level"] = data["level"]
    if data.get("points_to_win") in settings.POINT_CHOICES:
        config["points_to_win"] = data["points_to_win"]
    return config


def save(config, path=None):
    """Écrit les réglages ; renvoie False si l'écriture est impossible."""
    path = Path(path) if path else config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return False
    return True
```

### `main.py`

```python
"""Point d'entrée du jeu.

Lancement : `python main.py`
"""

import sys
from pathlib import Path

from pong.app import App

LOG_NAME = "pong-error.log"


def report_startup_error(message, log_dir=None):
    """Signale une erreur de démarrage là où l'utilisateur peut la voir."""
    print(message, file=sys.stderr)

    log_path = Path(log_dir) if log_dir else Path.cwd()
    log_path = log_path / LOG_NAME
    try:
        log_path.write_text(message + "\n", encoding="utf-8")
    except OSError:
        log_path = None
    else:
        print(f"Détail écrit dans {log_path}", file=sys.stderr)

    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                None, message, "Pong — démarrage impossible", 0x10)
        except Exception:
            pass

    return log_path


def main():
    """Lance le jeu ; renvoie le code de sortie du processus."""
    try:
        app = App()
    except Exception as error:  # mieux vaut un message qu'une fermeture muette
        report_startup_error(f"Pong n'a pas pu démarrer :\n{error}")
        return 1
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `tests/test_config.py` (extraits)

```python
"""Tests des réglages persistants."""

import json

from pong import config, settings


def test_missing_file_falls_back_to_defaults(tmp_path):
    loaded = config.load(tmp_path / "absent.json")

    assert loaded["level"] == "moyen"
    assert loaded["points_to_win"] == settings.POINTS_TO_WIN


def test_corrupted_file_falls_back_to_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{ pas du json", encoding="utf-8")

    assert config.load(path)["level"] == "moyen"


def test_invalid_values_are_ignored(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"level": "impossible", "points_to_win": 999}),
                    encoding="utf-8")

    loaded = config.load(path)

    assert loaded["level"] == "moyen"
    assert loaded["points_to_win"] == settings.POINTS_TO_WIN


def test_save_then_load_round_trip(tmp_path):
    path = tmp_path / "config.json"

    config.save({"level": "difficile", "points_to_win": 3}, path)

    loaded = config.load(path)
    assert loaded == {"level": "difficile", "points_to_win": 3}
```

## En résumé

- Un halo néon, c'est du texte atténué répété en décalage, puis le texte net.
- Une police **embarquée** (et sa **licence**) garantit un rendu identique partout.
- Des réglages **validés** et un fichier corrompu qui retombe sur les défauts.
- Une erreur de démarrage doit **toujours** laisser une trace visible.
- PyInstaller **n'embarque pas** vos données : `--add-data` est obligatoire, avec le
  bon séparateur selon le système.

---

## 🎉 Fin du cours

Vous avez construit un jeu complet : boucle et scènes, raquettes, balle et physique,
collisions au pixel près, IA à trois niveaux, score, menu, options, sons, pause, fin
de partie, images, police et déploiement. Le tout **testé**.

### Et maintenant ?

Quelques idées pour continuer par vous-même :

- **Un écran de meilleurs scores**, sauvegardé dans le même dossier de config.
- **Une balle qui accélère** davantage, ou un mode « sudden death ».
- **Un power-up** : une balle qui grossit, une raquette qui rétrécit…
- **Des niveaux d'IA supplémentaires**, ou une IA qui apprend vos habitudes.
- **Du son** : une musique de fond, des bruitages différents selon la raquette.
- **Une traduction** : les libellés dans un fichier, et un choix de langue.

Le plus important n'est pas la liste : c'est la méthode. **Une responsabilité par
fichier, la logique séparée de l'affichage, et un test avant chaque fonctionnalité.**
Elle marche pour Pong… et pour tout le reste.

Bon code, et amusez-vous bien ! 🏓

---

→ Retour au [sommaire du cours](README.md)
