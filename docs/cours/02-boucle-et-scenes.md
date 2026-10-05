# 02 — La boucle et les scènes

## Objectifs

À la fin de ce chapitre, vous saurez :

- transformer votre script du chapitre 01 en une **classe `App`** réutilisable ;
- comprendre le **delta time** (`dt`) et pourquoi il rend le jeu indépendant du
  matériel ;
- créer des **scènes** (menu, partie, pause…) que l'`App` fait tourner ;
- centraliser les constantes dans `settings.py`.

**Fichiers du projet :** `main.py`, `pong/app.py`, `pong/scenes/base.py`, `pong/scenes/menu.py`, `pong/settings.py`
**Test du projet :** `tests/test_app_smoke.py`

## 1. Du script à l'application

Au chapitre 01, tout tenait dans `main.py`. Ça fonctionne, mais un jeu complet a
besoin de plusieurs écrans (menu, partie, pause, fin) et d'un état (score, scène
courante…). Garder tout dans une seule boucle deviendrait vite illisible.

Nous allons donc créer une classe **`App`** qui possède la fenêtre, l'horloge et la
scène courante, et qui contient **la boucle**. `main.py` se réduira à trois lignes.

## 2. `settings.py` : les constantes au même endroit

Première brique : un module qui ne contient **que** des valeurs réglables.

```python
"""Constantes globales du jeu.

Ce module ne contient aucune logique : uniquement des valeurs de configuration,
regroupées ici pour être ajustées en un seul endroit.
"""

# --- Fenêtre ---
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FPS = 60
CAPTION = "Pong"
```

> 💡 **Pourquoi un fichier dédié ?** Imaginez `900` recopié dans huit fichiers :
> pour changer la taille de la fenêtre, il faudrait tous les retrouver. Ici, une
> seule ligne à modifier.

## 3. La classe `App`

```python
class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        pygame.display.set_caption(settings.CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True
```

- `self.screen` est la **surface** de la fenêtre : c'est là qu'on dessine.
- `self.clock` servira à cadrer la cadence.
- `self.running` est le drapeau qui maintient la boucle en vie.

## 4. Le delta time : la clé d'un jeu fluide

Au chapitre 01, on appelait `clock.tick(60)` sans utiliser sa valeur de retour. Or
`tick()` renvoie le **nombre de millisecondes écoulées** depuis l'image précédente.

```python
dt = min(self.clock.tick(settings.FPS) / 1000.0, 0.05)
```

- On divise par 1000 pour obtenir des **secondes**.
- `min(..., 0.05)` **plafonne** `dt` à 50 ms.

Pourquoi est-ce capital ? Imaginez une balle qui avance de « 5 pixels par image » :

| Écran | Images/s | Distance en 1 s |
|-------|----------|-----------------|
| classique | 60 | 300 px |
| jeu rapide | 144 | 720 px ❌ |

La balle irait plus de deux fois plus vite selon le matériel ! En exprimant les
vitesses en **pixels par seconde** et en multipliant par `dt`, tout le monde joue
à la même vitesse :

```python
self.x += self.vx * dt        # vx en pixels/seconde
```

Le plafond de 50 ms évite un autre problème : si vous déplacez la fenêtre ou si la
machine est occupée, `dt` peut devenir énorme et la balle « sauterait » à travers
les murs au retour.

## 5. Les scènes

Un jeu a plusieurs écrans. Plutôt qu'un gros `if` pour savoir lequel dessiner, on
utilise des **scènes** : chacune est un objet avec trois méthodes.

```python
class Scene:
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        """Réagit à un événement pygame (clavier, fermeture...)."""

    def update(self, dt):
        """Met à jour la logique de la scène (dt en secondes)."""

    def draw(self, surface):
        """Dessine la scène sur `surface`."""
```

Ces trois méthodes correspondent exactement aux trois temps de la boucle :
**événements → mise à jour → dessin**.

L'`App` ne connaît que **la** scène courante et lui délègue tout :

```python
def switch_scene(self, name, **kwargs):
    """Construit une nouvelle scène et l'active."""
    self.scene = self._scenes[name](self, **kwargs)

def set_scene(self, scene):
    """Active une scène déjà construite (reprise après pause)."""
    self.scene = scene
```

La différence entre les deux est importante :

- `switch_scene` **construit** une scène neuve (par exemple, quitter le menu pour
  commencer une partie).
- `set_scene` **réactive** une scène existante — c'est ce qui permettra de
  reprendre une partie après une pause **sans la recréer**.

## 6. La boucle complète

```python
def run(self):
    try:
        while self.running:
            dt = min(self.clock.tick(settings.FPS) / 1000.0, 0.05)
            # On fige la scène du début d'image.
            scene = self.scene
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    break
                scene.handle_event(event)
            else:
                scene.update(dt)
                scene.draw(self.screen)
                pygame.display.flip()
    finally:
        pygame.quit()
```

Deux subtilités :

- **`scene = self.scene`** fige la scène du début d'image. Sans cela, un événement
  qui change de scène redirigerait les événements **suivants de la même image**
  vers la nouvelle scène — source de bugs très difficiles à trouver.
- **`for ... else`** : le `else` ne s'exécute que si la boucle `for` n'a pas été
  interrompue par un `break`. Autrement dit, si on vient de fermer la fenêtre, on
  **saute** la mise à jour et le dessin de cette image.

## À vous de jouer !

Reprenez le code du chapitre 01 et transformez-le :

1. Créez `pong/settings.py` avec les quatre constantes ci-dessus.
2. Créez `pong/scenes/base.py` avec la classe `Scene`.
3. Créez `pong/scenes/menu.py` avec une `MenuScene` qui, pour l'instant, se
   contente de remplir l'écran d'une couleur sombre (par exemple `(18, 6, 46)`).
4. Créez `pong/app.py` avec la classe `App` (fenêtre, horloge, scènes, boucle).
5. Réduisez `main.py` à : créer une `App` et appeler `run()`.

**Vérification :** `python main.py` doit ouvrir une fenêtre sombre qui se ferme
proprement. Puis écrivez un **test de fumée** qui démarre l'application sans
écran réel (voir le corrigé) : c'est votre premier test, et il vérifie que le
squelette du jeu tient debout.

<details>
<summary>Un indice pour le test</summary>

En environnement sans écran, pygame a besoin d'un pilote vidéo factice. On le
choisit avec une variable d'environnement :

```python
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
```

Placez-la dans `tests/conftest.py` : pytest l'appliquera à tous les tests.

</details>

## Corrigé

### `pong/settings.py`

```python
"""Constantes globales du jeu.

Ce module ne contient aucune logique : uniquement des valeurs de configuration,
regroupées ici pour être ajustées en un seul endroit.
"""

# --- Fenêtre ---
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FPS = 60
CAPTION = "Pong"
```

### `pong/scenes/base.py`

```python
"""Classe de base des scènes.

Une scène représente un écran ou un état du jeu (menu, partie, pause, fin).
L'`App` délègue à la scène courante les événements, la mise à jour et le dessin.
"""


class Scene:
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        """Réagit à un événement pygame (clavier, fermeture de fenêtre...)."""

    def update(self, dt):
        """Met à jour la logique de la scène (dt en secondes)."""

    def draw(self, surface):
        """Dessine la scène sur `surface`."""
```

### `pong/scenes/menu.py` (version minimale)

```python
"""Menu principal (version minimale du chapitre 02)."""

from .base import Scene


class MenuScene(Scene):
    """Écran d'accueil, vide pour l'instant."""

    def draw(self, surface):
        surface.fill((18, 6, 46))
```

### `pong/app.py`

```python
"""Application : initialisation, boucle principale et gestion des scènes."""

import pygame

from . import settings
from .scenes.menu import MenuScene


class App:
    """Possède la fenêtre, l'horloge et la scène courante."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        pygame.display.set_caption(settings.CAPTION)

        self.clock = pygame.time.Clock()
        self.running = True

        self._scenes = {"menu": MenuScene}
        self.scene = None
        self.switch_scene("menu")

    def switch_scene(self, name, **kwargs):
        """Construit une nouvelle scène et l'active."""
        self.scene = self._scenes[name](self, **kwargs)

    def set_scene(self, scene):
        """Active une scène déjà construite (ex. reprise après pause)."""
        self.scene = scene

    def quit(self):
        self.running = False

    def run(self):
        """Boucle principale, jusqu'à la fermeture de la fenêtre."""
        try:
            while self.running:
                # dt plafonné : évite un saut énorme après une pause système.
                dt = min(self.clock.tick(settings.FPS) / 1000.0, 0.05)
                # On fige la scène du début d'image : un changement de scène en
                # cours d'événement ne doit pas rediriger le reste de l'image.
                scene = self.scene
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                        break
                    scene.handle_event(event)
                else:
                    scene.update(dt)
                    scene.draw(self.screen)
                    pygame.display.flip()
        finally:
            pygame.quit()
```

### `main.py`

```python
"""Point d'entrée du jeu.

Lancement : `python main.py`
"""

from pong.app import App


def main():
    App().run()


if __name__ == "__main__":
    main()
```

### `tests/conftest.py`

```python
"""Réglages communs aux tests : pilotes SDL factices (pas d'écran requis)."""

import os

# Permet de créer une fenêtre pygame et un mixer audio sans matériel réel.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
```

### `tests/test_app_smoke.py`

```python
"""Test de fumée : le squelette de l'application démarre sans écran."""

from pong.app import App
from pong.scenes.menu import MenuScene


def test_app_starts_on_the_menu_and_draws():
    app = App()

    assert isinstance(app.scene, MenuScene)
    app.scene.draw(app.screen)   # ne doit pas lever d'erreur
    app.quit()
```

Lancez :

```bash
pytest
```

Vous devez voir `1 passed`. Bravo : vous avez votre premier test.

> **Dans le projet de référence :** `pong/app.py` est bien plus complet à la fin du
> cours (assets, polices, son, réglages). Nous l'enrichirons chapitre après
> chapitre — c'est exactement comme cela qu'on construit un jeu.

## En résumé

- L'`App` possède la fenêtre et **la boucle** ; `main.py` ne fait que la lancer.
- `dt` (en secondes) rend le jeu indépendant de la vitesse de la machine.
- Une **scène** expose `handle_event`, `update`, `draw`.
- `switch_scene` crée une scène ; `set_scene` en réactive une.
- `for ... else` et la variable locale `scene` évitent deux bugs classiques.

## Étape suivante

→ [03 — Les raquettes](03-les-raquettes.md)
