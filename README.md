<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.6-1B75BB?style=for-the-badge" alt="pygame">
  <img src="https://img.shields.io/badge/Th%C3%A8me-Cyberpunk-FF2E95?style=for-the-badge" alt="Thème cyberpunk">
  <img src="https://img.shields.io/badge/Licence-MIT-green?style=for-the-badge" alt="Licence MIT">
</p>

<p align="center">
  <a href="https://github.com/Lamizana/Pong/actions/workflows/build.yml">
    <img src="https://github.com/Lamizana/Pong/actions/workflows/build.yml/badge.svg?branch=main" alt="CI — Build & tests">
  </a>
</p>

<h1 align="center">Pong</h1>

<p align="center">
  <strong>Jeu Pong en Python (pygame) — 1 ou 2 joueurs</strong>
</p>

<p align="center">
  <em>Déployable en exécutable Linux &amp; Windows, avec un tutoriel complet en français</em>
</p>

---

## A propos

**Pong** est un jeu d'arcade complet écrit en **Python** avec **pygame**. Il propose un
mode **un joueur** face à une IA à trois niveaux de difficulté, ou un mode **deux
joueurs** en local sur le même clavier.

Le projet est pensé comme un **exemple pédagogique** : la logique du jeu (physique, IA,
score) est **séparée de l'affichage**, entièrement **testée**, et accompagnée d'un
**tutoriel pas à pas en français**. Il se déploie en **exécutable autonome** (Linux et
Windows) via PyInstaller et GitHub Actions.

Le tout habillé d'un thème **cyberpunk** : fond illustré (ville néon, portail
doré, grille en perspective), raquettes mécaniques, balle cybernétique — des
images générées par IA chargées comme assets.

---

## Apercu

<p align="center">
  <img src="docs/screenshots/game.png" alt="Aperçu du jeu Pong (thème cyberpunk)" width="760">
</p>

---

## Table des matieres

- [A propos](#a-propos)
- [Apercu](#apercu)
- [Fonctionnalites](#fonctionnalites)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Installation et lancement](#installation-et-lancement)
  - [Prerequis](#prerequis)
  - [Lancement](#lancement)
  - [Controles](#controles)
  - [Tests](#tests)
- [Packaging et deploiement](#packaging-et-deploiement)
- [Tutoriel](#tutoriel)
- [Licence](#licence)

---

## Fonctionnalites

| Fonctionnalite | Description |
| --- | --- |
| **2 modes de jeu** | 1 joueur contre l'IA, ou 2 joueurs en local |
| **IA a 3 niveaux** | Facile, Moyen, Difficile (vitesse et précision réglables) |
| **Menu principal** | Sélection du mode, navigation clavier, relance de partie |
| **Score et victoire** | Premier à 5 points (réglable : 3, 5 ou 10), écran de fin avec rejeu |
| **Physique de rebond avancée** | L'angle de la balle dépend du point d'impact sur la raquette |
| **Sons générés en code** | Bruitages synthétisés, aucun fichier audio requis |
| **Pause** | Reprise exactement où la partie s'était arrêtée |
| **Theme cyberpunk** | Fond illustré (ville néon, portail doré, grille), raquettes mécaniques, balle cybernétique, halos néon |
| **Tests automatises** | Physique, IA, score et parcours des scènes, sans ouvrir de fenêtre |
| **Packaging multiplateforme** | Exécutables Linux et Windows via PyInstaller + GitHub Actions |

---

## Stack technique

| Categorie | Technologie | Badge |
| --- | --- | --- |
| **Langage** | Python 3.10+ | ![](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white) |
| **Moteur de jeu** | pygame 2.6 | ![](https://img.shields.io/badge/pygame-2.6-1B75BB) |
| **Tests** | pytest | ![](https://img.shields.io/badge/pytest-9-0A9EDC?logo=pytest&logoColor=white) |
| **Packaging** | PyInstaller | ![](https://img.shields.io/badge/PyInstaller-6-FFD43B) |
| **CI/CD** | GitHub Actions | ![](https://img.shields.io/badge/GitHub_Actions-build-2088FF?logo=githubactions&logoColor=white) |
| **Licence** | MIT | ![](https://img.shields.io/badge/Licence-MIT-green) |

---

## Structure du projet

```console
Pong/
├── main.py                      # Point d'entrée : « python main.py »
├── pong/
│   ├── settings.py              # Toutes les constantes (écran, couleurs, vitesses...)
│   ├── ball.py                  # Balle : déplacement, rebonds, physique
│   ├── paddle.py                # Raquettes : déplacement borné
│   ├── ai.py                    # Adversaire automatique (3 niveaux)
│   ├── score.py                 # Score et condition de victoire
│   ├── sound.py                 # Génération et lecture des sons
│   ├── collision.py             # Contact cercle/rectangle (balle vs raquette)
│   ├── synthwave.py             # Texte néon (halo diffus + texte net)
│   ├── resources.py             # Chargement des assets (images, police)
│   ├── assets/                  # Images PNG + police Orbitron (et sa licence)
│   ├── app.py                   # Fenêtre, boucle de jeu, gestion des scènes
│   └── scenes/                  # Menu, options, partie, pause, fin de partie
├── scripts/
│   ├── render_preview.py        # Génère les aperçus PNG
│   └── prepare_assets.py        # Détoure/redimensionne les images sources
├── images/                      # Images sources (JPEG, hors dépôt)
├── tests/                       # Tests pytest
├── docs/
│   ├── tutoriel/                # Tutoriel complet (12 chapitres)
│   └── screenshots/             # Captures d'écran
├── build.sh / build.ps1         # Création des exécutables
└── .github/workflows/build.yml  # CI : tests + builds Linux & Windows
```

---

## Installation et lancement

### Prerequis

- **Python 3.10 ou plus récent**
- `pip` (ou [`uv`](https://github.com/astral-sh/uv) pour aller plus vite)

### Lancement

```bash
# 1. Environnement virtuel + dépendances
uv venv && uv pip install -r requirements-dev.txt
# ou :
# python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt

# 2. Lancer le jeu
python main.py
```

### Controles

| Action | Joueur 1 | Joueur 2 | General |
| --- | --- | --- | --- |
| Monter | `Z` ou `W` | `↑` | |
| Descendre | `S` | `↓` | |
| Naviguer dans les menus | `↑` / `↓`, `Z` / `S` | | |
| Valider | | | `Entree` (ou `Espace`) |
| Pause / reprendre | | | `P` ou `Echap` |
| Retour au menu | | | `Q` ou `M` |

### Tests

```bash
pytest
```

Les tests couvrent la physique de la balle, les raquettes, l'IA, le score, la génération
des sons, les collisions, le prétraitement des images, la cohérence de la documentation
et le parcours complet des scènes — **sans fenêtre**.

---

## Packaging et deploiement

```bash
./build.sh        # Linux  -> dist/Pong
```

```powershell
.\build.ps1       # Windows -> dist\Pong.exe
```

> **Important** : PyInstaller ne compile pas pour un autre système. Le `.exe` Windows
> doit être produit **sous Windows** — c'est la **CI GitHub Actions** qui s'en charge à
> chaque `push` sur `main`, à chaque tag `v*`, ou manuellement. Les exécutables sont
> ensuite téléchargeables dans l'onglet **Actions** (artefacts `Pong-linux` et
> `Pong-windows`).

---

## Tutoriel

Un tutoriel complet en français, un chapitre par étape, se trouve dans
**[`docs/tutoriel/`](docs/tutoriel/README.md)** :

00. Introduction · 01. Installation · 02. Structure · 03. Boucle de jeu ·
04. Raquettes · 05. Balle et physique · 06. IA · 07. Score et victoire ·
08. Menu et scènes · 09. Sons · 10. Pause · 11. Packaging et déploiement ·
12. Style rétro synthwave

---

## Licence

Distribué sous licence **MIT** — libre d'utilisation, de modification et de partage.
