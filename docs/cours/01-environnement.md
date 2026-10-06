# 01 — L'environnement

## Objectifs

À la fin de ce chapitre, vous saurez :

- vérifier que Python est installé ;
- créer un **environnement virtuel** et y installer pygame ;
- installer **pytest**, l'outil qui lancera nos tests ;
- créer la **structure de dossiers** du projet ;
- afficher votre **première fenêtre** avec pygame, qui se ferme proprement.

## 1. Vérifier Python

Ouvrez un terminal et tapez :

```bash
python3 --version
```

Vous devez voir `Python 3.10` ou plus récent. Sinon, installez Python depuis
[python.org](https://www.python.org/downloads/) (sous Windows, cochez « Add Python
to PATH » pendant l'installation).

## 2. Créer le dossier du projet

```bash
mkdir pong
cd pong
```

Tous les fichiers du cours vivront dans ce dossier.

## 3. Un environnement virtuel

Un **environnement virtuel** est une copie isolée de Python, avec ses propres
bibliothèques. Cela évite de polluer votre système et de mélanger les versions
entre projets.

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Le prompt du terminal affiche maintenant `(.venv)`. C'est bon signe : tout ce qu'on
installera ira **dans ce dossier**.

## 4. Installer pygame et pytest

pygame fournit la fenêtre, le dessin, le son et les événements clavier.
pytest fait tourner les tests.

Créez un fichier `requirements.txt` :

```text
pygame>=2.5,<3
```

Puis installez :

```bash
pip install -r requirements.txt
pip install "pytest>=8,<10"
```

Vérifions que tout fonctionne :

```bash
python -c "import pygame; print(pygame.version.ver)"
```

## 5. La structure du projet

Créez dès maintenant l'arborescence. Le paquet `pong/` contiendra la logique, et
`tests/` les tests.

```console
pong/                       ← le dossier du projet
├── main.py                 ← point d'entrée
├── requirements.txt
├── pong/                   ← le paquet (la logique et l'affichage)
│   ├── __init__.py         ← marque le dossier comme paquet Python
│   ├── settings.py         ← les constantes (chapitre 02)
│   └── scenes/             ← les écrans (chapitre 02)
│       ├── __init__.py
│       └── base.py
└── tests/
    └── conftest.py         ← réglages communs aux tests (plus bas)
```

Sous Linux/macOS :

```bash
mkdir -p pong/scenes tests
touch pong/__init__.py pong/scenes/__init__.py
```

Sous Windows (PowerShell) :

```powershell
mkdir pong\scenes, tests
New-Item pong\__init__.py, pong\scenes\__init__.py -ItemType File
```

> 💡 **Pourquoi un dossier `pong/` dans le dossier `pong/` ?** Le dossier externe
> est *le projet*, le dossier interne est *le paquet* (la partie importable :
> `from pong.app import App`). C'est une convention courante en Python.

## À vous de jouer

Écrivez `main.py` pour qu'il :

1. ouvre une fenêtre de **900 × 600** pixels avec le titre **« Pong »** ;
2. reste ouverte, à **60 images par seconde**, sur un fond sombre ;
3. se ferme **proprement** quand on clique sur la croix de la fenêtre.

Pour cela, vous aurez besoin de :

- `pygame.init()` pour démarrer pygame ;
- `pygame.display.set_mode((largeur, hauteur))` pour créer la fenêtre ;
- `pygame.display.set_caption("Pong")` pour son titre ;
- `pygame.time.Clock()` et `clock.tick(60)` pour limiter la cadence ;
- `pygame.event.get()` et l'événement `pygame.QUIT` pour détecter la fermeture ;
- `screen.fill(couleur)` et `pygame.display.flip()` pour dessiner ;
- `pygame.quit()` à la fin, dans un `finally` (voir plus bas).

Essayez seul(e) avant de lire le corrigé. Même si vous tâtonnez, vous apprendrez
plus qu'en lisant.

<details>
<summary>Un indice (cliquez pour déplier)</summary>

La structure d'un programme pygame est presque toujours :

```python
running = True
while running:
    # 1. lire les événements
    # 2. mettre à jour le monde
    # 3. dessiner
```

</details>

## Corrigé

```python
"""Point d'entrée minimal : une fenêtre qui s'ouvre et se ferme proprement."""

import pygame

WIDTH, HEIGHT = 900, 600
FPS = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()

    running = True
    try:
        while running:
            clock.tick(FPS)

            # 1. Les événements : tout ce qui s'est passé depuis l'image précédente.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 2. Le dessin : on remplit l'écran, puis on l'affiche.
            screen.fill((18, 6, 46))
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
```

Décortiquons-le.

### `pygame.init()` et la fenêtre

`pygame.init()` démarre les sous-systèmes (affichage, son, polices).
`pygame.display.set_mode((900, 600))` ouvre la fenêtre et renvoie sa **surface** :
la zone de pixels sur laquelle on dessine. Tout ce qu'on « dessine » l'est en
réalité sur cette surface, en mémoire — jusqu'à ce qu'on l'affiche.

### La boucle de jeu

Un jeu est une boucle qui tourne des dizaines de fois par seconde : lire les
entrées, mettre à jour, dessiner, recommencer. La nôtre se répète tant que
`running` vaut `True`.

### `clock.tick(FPS)`

`tick(60)` attend le temps nécessaire pour ne pas dépasser 60 images par seconde.
Sans lui, la boucle tournerait à plusieurs milliers de tours par seconde et
saturerait un processeur pour rien.

### La file d'événements

`pygame.event.get()` renvoie la liste de tout ce qui s'est passé depuis l'image
précédente : touches pressées, clic sur la croix… On cherche ici l'événement
`pygame.QUIT`, déclenché par la fermeture de la fenêtre, et on arrête la boucle.

### `fill` puis `flip`

`screen.fill(...)` efface tout l'écran avec une couleur — sans cela, le dessin de
l'image précédente resterait visible. `pygame.display.flip()` envoie le résultat à
l'écran. **Si vous oubliez `flip()`, rien ne s'affiche jamais.**

### Le `try / finally`

```python
try:
    ...  # la boucle
finally:
    pygame.quit()
```

Le bloc `finally` s'exécute **toujours**, même en cas d'erreur. C'est la garantie
que pygame est refermé proprement, quoi qu'il arrive.

### `if __name__ == "__main__":`

Cette condition est vraie quand on exécute le fichier directement
(`python main.py`), fausse quand on l'importe depuis un test. C'est le réflexe à
avoir pour un point d'entrée.

### Lancer le jeu

```bash
python main.py
```

Une fenêtre sombre doit s'ouvrir. Fermez-la : le programme se termine sans erreur.

## En résumé

- On travaille toujours dans un **environnement virtuel** (`.venv`).
- Un programme pygame s'articule autour d'une **boucle** : événements → mise à
  jour → dessin.
- `pygame.display.flip()` rend le dessin visible, et `try / finally` garantit
  `pygame.quit()`.
- Le paquet `pong/` contiendra la logique ; `tests/` les tests.

> **Dans le projet de référence :** ce premier jet correspond à `main.py` du
> chapitre 01. Au chapitre 02, il devient un `main.py` de trois lignes et une vraie
> classe `App` dans `pong/app.py`.

## Étape suivante

→ [02 — La boucle et les scènes](02-boucle-et-scenes.md)
