# 02 — Structure du projet

Avant d'écrire la moindre ligne de jeu, mettons en place une arborescence claire.
Un projet bien rangé est un projet qu'on peut rouvrir trois mois plus tard sans
s'arracher les cheveux.

## L'arborescence

```
Pong/
├── main.py                       # point d'entrée : « python main.py »
├── pong/                         # le code du jeu (un package Python)
│   ├── __init__.py               # marque pong/ comme un package
│   ├── settings.py               # toutes les constantes
│   ├── ball.py                   # la balle et sa physique
│   ├── paddle.py                 # les raquettes
│   ├── ai.py                     # l'adversaire automatique
│   ├── score.py                  # score et condition de victoire
│   ├── sound.py                  # génération et lecture des sons
│   ├── app.py                    # fenêtre, boucle, gestion des scènes
│   └── scenes/                   # les écrans du jeu
│       ├── base.py               # classe Scene commune
│       ├── menu.py               # menu principal
│       ├── game.py               # déroulement d'une partie
│       ├── pause.py              # overlay de pause
│       └── gameover.py           # écran de fin
├── tests/                        # tests automatisés (pytest)
├── docs/tutoriel/                # ce tutoriel
├── requirements.txt              # dépendances d'exécution
├── requirements-dev.txt          # dépendances de développement
├── pyproject.toml                # métadonnées + config pytest
├── build.sh / build.ps1          # création des exécutables
└── .github/workflows/build.yml   # CI : builds Linux + Windows
```

## Pourquoi un dossier `pong/` ?

En Python, un dossier contenant un fichier `__init__.py` est un **package** : on
peut importer ses modules avec la notation pointée.

```python
from pong.ball import Ball
from pong.scenes.game import GameScene
```

Cela évite les collisions de noms avec d'autres bibliothèques et rend les imports
sans ambiguïté.

## Le rôle de chaque module

| Module | Responsabilité unique |
|--------|-----------------------|
| `settings.py` | Stocker les valeurs de configuration (aucune logique). |
| `ball.py` | Déplacer la balle, gérer ses rebonds. |
| `paddle.py` | Déplacer une raquette en la gardant à l'écran. |
| `ai.py` | Décider où déplacer la raquette adverse. |
| `score.py` | Compter les points et détecter la victoire. |
| `sound.py` | Générer et jouer les bruitages. |
| `app.py` | Faire tourner la boucle et changer de scène. |
| `scenes/*` | Afficher et réagir, une scène par écran. |

## Règle d'or : logique d'un côté, affichage de l'autre

Regarde la frontière entre `ball.py` et `scenes/game.py` :

- `ball.py` connaît la *position* et la *vitesse* de la balle. Il ne sait pas
  qu'elle est dessinée en bleu.
- `scenes/game.py` sait *comment dessiner* la balle. Il ne décide pas de sa
  trajectoire.

Cette séparation a un bénéfice très concret : on peut tester la physique **sans
écran ni fenêtre**, ce qui rend les tests rapides et fiables, y compris sur un
serveur d'intégration continue.

## Le fichier `settings.py`

Toutes les constantes vivent ici. Par exemple :

```python
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FPS = 60

PADDLE_HEIGHT = 100
PADDLE_SPEED = 520          # pixels par seconde

BALL_START_SPEED = 360
BALL_SPEEDUP = 22
BALL_MAX_SPEED = 820
MAX_BOUNCE_ANGLE = 60       # degrés

POINTS_TO_WIN = 7
```

Tu veux une balle plus rapide ou un écran plus grand ? Un seul endroit à modifier.

**Deux unités à retenir pour tout le projet :**

- Les **positions** sont en **pixels**.
- Les **vitesses** sont en **pixels par seconde**.

On multipliera systématiquement les vitesses par un intervalle de temps (`dt`) pour
que le jeu se comporte pareil, que l'ordinateur tourne à 30 ou 144 images par
seconde. Nous verrons cela au chapitre suivant.

## Étape suivante

→ [03 — La boucle de jeu](03-boucle-de-jeu.md)
