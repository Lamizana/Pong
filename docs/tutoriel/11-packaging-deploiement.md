# 11 — Packaging et déploiement

Le jeu fonctionne. Il ne reste plus qu'à le transformer en **exécutable** que l'on
peut lancer sans installer Python. C'est le rôle de **PyInstaller**.

## Pourquoi PyInstaller ?

PyInstaller analyse le programme, rassemble l'interpréteur Python, la bibliothèque
pygame et les dépendances dans un **fichier unique**. L'utilisateur final n'a plus
qu'à double-cliquer : aucun `pip install` nécessaire.

## Une contrainte à connaître absolument

PyInstaller **n'est pas un compilateur croisé**. Il produit un exécutable pour le
système sur lequel il s'exécute :

- sous **Linux**, il produit un binaire Linux ;
- sous **Windows**, il produit un `.exe` Windows ;
- sous **macOS**, il produit une application macOS.

Autrement dit, **on ne crée pas un `.exe` Windows depuis une machine Linux**. Pour
obtenir les deux, on dispose de deux solutions :

1. builder sur chaque système (utile pour Linux, où l'on travaille) ;
2. laisser une **intégration continue** (GitHub Actions) builder sur les deux, ce qui
   est la méthode propre pour obtenir le `.exe` sans posséder de PC Windows.

## La commande de base

```bash
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Pong main.py
```

| Option | Effet |
|--------|-------|
| `--onefile` | Regroupe tout en **un seul** fichier exécutable. |
| `--windowed` | Pas de console en arrière-plan (mode graphique). Essentiel sous Windows. |
| `--name Pong` | Nomme l'exécutable `Pong` (ou `Pong.exe`). |
| `--noconfirm` | Écrase les sorties précédentes sans demander. |
| `--clean` | Repart d'un dossier de travail propre. |

Le résultat apparaît dans `dist/`. Les fichiers intermédiaires vont dans `build/`
(tous deux ignorés par git).

## Les scripts fournis

### Linux — `build.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
fi

"$PYTHON" -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name Pong main.py

echo "Terminé : dist/Pong"
```

Le script utilise automatiquement le Python du `.venv` s'il existe. `set -euo pipefail`
garantit qu'il s'arrête à la moindre erreur.

### Windows — `build.ps1`

```powershell
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }

& $python -m PyInstaller --noconfirm --clean --onefile --windowed --name Pong main.py

Write-Host "Terminé : dist\Pong.exe"
```

## La CI GitHub Actions

Le workflow `.github/workflows/build.yml` teste et build sur les deux systèmes :

```yaml
jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            artifact: Pong-linux
            binary: dist/Pong
          - os: windows-latest
            artifact: Pong-windows
            binary: dist/Pong.exe
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements-dev.txt
      - run: python -m pytest
      - shell: bash
        run: |
          python -m PyInstaller --noconfirm --clean --onefile --windowed \
            --name Pong main.py
      - uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact }}
          path: ${{ matrix.binary }}
```

Ce workflow se déclenche :

- à chaque `push` sur `main` ;
- à chaque **tag** `v...` (par exemple `v1.0.0`, une vraie « release ») ;
- manuellement, via `workflow_dispatch`.

La **matrice** (`matrix`) lance les deux jobs en parallèle. Après exécution, les
exécutables sont téléchargeables dans l'onglet **Actions** de GitHub, sous forme
d'**artefacts**.

## Publier une version

```bash
git tag v1.0.0
git push origin v1.0.0
```

1. La CI se déclenche.
2. Elle lance les tests, build sous Linux et sous Windows.
3. Tu récupères `Pong-linux` et `Pong-windows` dans les artefacts.

C'est ainsi que l'on obtient un `.exe` Windows sans jamais lancer Windows soi-même.

## Vérifier un build local

```bash
./build.sh
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 3 ./dist/Pong
```

Si le jeu s'exécute trois secondes sans erreur (arrêté par `timeout`), le binaire est
sain. C'est exactement la vérification qui a été faite sur ce projet.

## En résumé

- **`pyinstaller`** crée l'exécutable. `--onefile --windowed` pour une application
  graphique autonome.
- **Pas de build croisé** : chaque OS doit builder le sien.
- **GitHub Actions** automatise les deux builds, et les tests, à chaque version.

Félicitations, ton Pong est maintenant un vrai logiciel distribuable ! 🏓

---

[Retour au sommaire du tutoriel](README.md)
