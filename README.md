# Pong 🏓

Un jeu **Pong** complet en **Python** (pygame), jouable à **1 joueur** (contre une IA
à 3 niveaux de difficulté) ou à **2 joueurs**, et déployable en **exécutable Linux et
Windows**.

Ce dépôt contient aussi un **tutoriel détaillé en français** qui explique comment le
jeu a été construit, étape par étape.

## Fonctionnalités

- 🎮 **2 modes** : 1 joueur (IA facile / moyen / difficile) ou 2 joueurs.
- 📋 **Menu principal** de sélection du mode.
- 🏆 **Score et condition de victoire** (premier à 7 points).
- 🎯 **Physique de rebond avancée** : l'angle dépend du point d'impact sur la raquette.
- 🔊 **Sons générés en code** (aucun fichier audio requis).
- ⏸️ **Pause** (reprise exactement où l'on s'était arrêté).
- ✅ **45 tests automatisés** sur la logique du jeu.

## Installation

```bash
# Environnement virtuel + dépendances
uv venv && uv pip install -r requirements-dev.txt
# ou :
# python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt
```

## Lancer le jeu

```bash
python main.py
```

## Contrôles

| Action | Joueur 1 | Joueur 2 | Général |
|--------|----------|----------|---------|
| Monter | `Z` ou `W` | `↑` | |
| Descendre | `S` | `↓` | |
| Naviguer dans les menus | `↑` / `↓`, `Z` / `S` | | |
| Valider | | | `Entrée` (ou `Espace`) |
| Pause / reprendre | | | `P` ou `Échap` |
| Retour au menu (pause) | | | `Q` |

## Tests

```bash
pytest
```

Les tests couvrent la physique de la balle, la raquette, l'IA, le score, la
génération des sons et le parcours complet des scènes — sans ouvrir de fenêtre.

## Créer un exécutable

```bash
./build.sh        # Linux  -> dist/Pong
```

```powershell
.\build.ps1       # Windows -> dist\Pong.exe
```

> ⚠️ PyInstaller ne compile pas pour un autre système : le `.exe` Windows doit être
> produit **sous Windows** (ou par la CI). Le workflow GitHub Actions
> (`.github/workflows/build.yml`) génère automatiquement les exécutables Linux et
> Windows, et lance les tests à chaque version.

## Structure du projet

```
Pong/
├── main.py                  # point d'entrée
├── pong/
│   ├── settings.py          # constantes du jeu
│   ├── ball.py              # balle et physique
│   ├── paddle.py            # raquettes
│   ├── ai.py                # adversaire automatique
│   ├── score.py             # score et victoire
│   ├── sound.py             # sons générés
│   ├── app.py               # fenêtre, boucle, scènes
│   └── scenes/              # menu, partie, pause, fin de partie
├── tests/                   # tests pytest
└── docs/tutoriel/           # tutoriel complet (FR)
```

## Tutoriel

Le tutoriel complet se trouve dans **[`docs/tutoriel/`](docs/tutoriel/README.md)** :

00. Introduction · 01. Installation · 02. Structure · 03. Boucle de jeu ·
04. Raquettes · 05. Balle et physique · 06. IA · 07. Score et victoire ·
08. Menu et scènes · 09. Sons · 10. Pause · 11. Packaging et déploiement

## Licence

MIT — libre d'utilisation, de modification et de partage.
