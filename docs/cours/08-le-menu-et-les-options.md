# 08 — Le menu et les options

## Objectifs

À la fin de ce chapitre, vous saurez :

- construire un **menu navigable** au clavier ;
- décrire les entrées du menu par une **liste de données** plutôt que par des `if` ;
- créer un **sous-menu de réglages** (difficulté, points pour gagner) ;
- partager un comportement entre plusieurs scènes (la **navigation**) sans le
  dupliquer ;
- transmettre des **paramètres** d'une scène à l'autre.

**Fichiers du projet :** `pong/scenes/menu.py`, `pong/scenes/options.py`, `pong/ui.py`
**Test du projet :** `tests/test_options_scene.py`, `tests/test_app_smoke.py`

## 1. Un menu, c'est une scène

Le menu est une scène comme une autre : il dessine, et il réagit au clavier. Sa
particularité est qu'il propose des **choix**.

Décrire ces choix par une **liste de tuples** rend le code très lisible :

```python
self.options = [
    ("1 joueur", "game", {"mode": "1p"}),
    ("2 joueurs", "game", {"mode": "2p"}),
    ("Options", "options", {}),
    ("Quitter", None, None),
]
```

Chaque ligne contient : le **libellé** affiché, le **nom de la scène** à activer, et
les **paramètres** à lui passer. Ajouter une entrée = ajouter une ligne. Et pour
afficher le menu, on n'a qu'un seul endroit à modifier :

```python
        ui.draw_choices(surface, self.app, frame_rect,
                        [label for label, _, _ in self.options], self.index)
```

## 2. Naviguer : l'index et le modulo

Le menu ne retient qu'**un nombre** : `self.index`, la ligne sélectionnée.

```python
self.index = (self.index + 1) % len(self.options)   # descend, et revient en haut
```

L'opérateur `%` (modulo) donne le **reste** de la division :

| `index` | `(index + 1) % 4` |
| --------- | ------------------- |
| 0 | 1 |
| 2 | 3 |
| **3** | **0** ← on boucle |

Ainsi, descendre depuis la dernière ligne ramène à la première, sans `if`. Et pour
monter, on utilise `(index - 1) % 4` — en Python, `-1 % 4` vaut bien `3`.

Le projet accepte **deux jeux de touches** pour naviguer : les flèches (joueur 2)
et Z/S ou W/S (joueur 1). On rassemble cela dans une petite fonction, pour ne pas
la répéter dans chaque scène :

```python
def navigation_index(event, index, count):
    """Nouvel index de sélection, ou None si l'événement n'est pas un déplacement."""
    if event.type != pygame.KEYDOWN:
        return None
    if event.key in settings.P1_UP or event.key in settings.P2_UP:
        return (index - 1) % count
    if event.key in settings.P1_DOWN or event.key in settings.P2_DOWN:
        return (index + 1) % count
    return None
```

> 💡 **Pourquoi renvoyer `None` plutôt que l'index inchangé ?** Parce que `None` veut
> dire « ce n'est pas un déplacement ». L'appelant peut alors essayer autre chose
> (valider, revenir…). Un index inchangé serait ambigu : « rien n'a bougé » ou
> « c'était une touche que je ne gère pas » ?

## 3. Valider un choix

```python
    def _select(self):
        _, scene_name, kwargs = self.options[self.index]
        if scene_name is None:
            self.app.quit()
        else:
            self.app.switch_scene(scene_name, **kwargs)
```

Deux cas particuliers élégants :

- `None` comme scène signifie **quitter** (l'entrée « Quitter »).
- `**kwargs` transmet les paramètres : `switch_scene("game", mode="1p")` appelle
  donc `GameScene(app, mode="1p")`.

## 4. Le sous-menu Options

L'écran Options est aussi un menu, mais chaque ligne porte une **valeur** qu'on fait
défiler avec ← et → :

```console
   > Difficulté : Moyen
     Points pour gagner : 5
     Retour
```

Les valeurs possibles viennent de `settings.py` :

```python
POINT_CHOICES = (3, 5, 10)   # valeurs proposées dans les options
AI_LEVELS = {"facile": {...}, "moyen": {...}, "difficile": {...}}
```

Et le changement se fait par **rotation circulaire** :

```python
    def _change(self, delta):
        config_now = self.app.config
        if self.index == _ROW_LEVEL:
            keys = list(settings.AI_LEVELS)
            config_now["level"] = keys[(keys.index(config_now["level"]) + delta) % len(keys)]
        elif self.index == _ROW_POINTS:
            choices = settings.POINT_CHOICES
            current = choices.index(config_now["points_to_win"])
            config_now["points_to_win"] = choices[(current + delta) % len(choices)]
        else:
            return   # ligne « Retour » : rien à changer
```

Le même `%` que pour la navigation : arrivé au bout de la liste, on repart au début.

## 5. Où stocker les réglages ?

Dans l'`App`, un simple dictionnaire :

```python
        # Réglages modifiables depuis les options (chapitre 12 : persistance).
        self.config = {"level": "moyen", "points_to_win": settings.POINTS_TO_WIN}
```

Les scènes y accèdent via `self.app.config` : la partie lit la difficulté et le
nombre de points au moment où elle démarre.

```python
class GameScene(Scene):
    def __init__(self, app, mode="1p"):
        ...
        self.level = app.config["level"]
        self.points_to_win = app.config["points_to_win"]
        self.ai = AI(level=self.level) if mode == "1p" else None
```

> 💡 Comme la difficulté n'est plus passée en paramètre, le menu devient plus
> simple : `switch_scene("game", mode="1p")` suffit.

## À vous de jouer

1. Créez `pong/ui.py` avec la fonction `navigation_index`.
2. Transformez `MenuScene` : quatre entrées, navigation, validation, et, depuis
   la pause, le retour au menu (`Q`/`M` — le chapitre 09 branche la pause).
3. Créez `OptionsScene` : deux lignes réglables et une ligne « Retour ».
4. Créez la scène `start` (l'écran d'accueil) et enregistrez-la dans
   `App._scenes` : le menu et les options y reviennent avec « Échap ».
5. Déclarez `"options"` dans `App._scenes` et ajoutez `app.config` dans `App`.
6. Écrivez les tests :
   - depuis le menu, choisir « Options » ouvre bien `OptionsScene` ;
   - « Échap », depuis le menu ou les options, ramène à l'écran d'accueil ;
   - dans les options, ← et → changent la valeur **et** bouclent (5 → 10 → 3) ;
   - la ligne « Retour » ramène au menu ;
   - `navigation_index` renvoie `None` pour une touche qui n'en est pas une.

<details>
<summary>Un indice sur les libellés affichés</summary>

On affiche « Difficulté : Moyen », mais la valeur stockée est `"moyen"`. La
traduction se fait à l'affichage, via le libellé du niveau :

```python
level = settings.AI_LEVELS[self.app.config["level"]]["label"]
```

</details>

## Corrigé

### `pong/ui.py`

```python
"""Helpers d'interface partagés par les écrans (menu, options, fin)."""

import pygame

from . import settings


def navigation_index(event, index, count):
    """Nouvel index de sélection, ou None si l'événement n'est pas un déplacement.

    Flèches haut/bas et Z/S/W (mêmes touches que les raquettes), avec bouclage.
    """
    if event.type != pygame.KEYDOWN:
        return None
    if event.key in settings.P1_UP or event.key in settings.P2_UP:
        return (index - 1) % count
    if event.key in settings.P1_DOWN or event.key in settings.P2_DOWN:
        return (index + 1) % count
    return None
```

### `pong/scenes/menu.py`

```python
"""Menu principal : lancement d'une partie et accès aux options."""

import pygame

from .. import settings, ui
from .base import Scene


class MenuScene(Scene):
    """Écran d'accueil : partie 1 joueur, 2 joueurs, options, quitter."""

    def __init__(self, app):
        super().__init__(app)
        # La difficulté et les points pour gagner se règlent dans les options.
        self.options = [
            ("1 joueur", "game", {"mode": "1p"}),
            ("2 joueurs", "game", {"mode": "2p"}),
            ("Options", "options", {}),
            ("Quitter", None, None),
        ]
        self.index = 0

    def handle_event(self, event):
        new_index = ui.navigation_index(event, self.index, len(self.options))
        if new_index is not None:
            self.index = new_index
        elif event.type == pygame.KEYDOWN and event.key in settings.KEY_HOME:
            self.app.switch_scene("start")
        elif event.type == pygame.KEYDOWN and event.key in settings.KEY_VALIDATE:
            self._select()

    def _select(self):
        _, scene_name, kwargs = self.options[self.index]
        if scene_name is None:
            self.app.quit()
        else:
            self.app.switch_scene(scene_name, **kwargs)

    def draw(self, surface):
        surface.fill((18, 6, 46))
        self.app.draw_text(surface, "PONG", self.app.font_large,
                           settings.NEON_YELLOW,
                           center=(settings.WINDOW_WIDTH // 2, 140))

        labels = [f"{'> ' if i == self.index else '  '}{label}"
                  for i, (label, _, _) in enumerate(self.options)]
        for i, label in enumerate(labels):
            color = settings.NEON_PINK if i == self.index else settings.TEXT_DIM
            self.app.draw_text(surface, label, self.app.font_small, color,
                               center=(settings.WINDOW_WIDTH // 2, 280 + i * 50))

        self.app.draw_text(surface, "↑/↓ ou Z/S : naviguer     Entrée : valider     Échap : accueil",
                           self.app.font_small, settings.TEXT_DIM,
                           center=(settings.WINDOW_WIDTH // 2,
                                   settings.WINDOW_HEIGHT - 30))
```

> 💡 Le dessin est volontairement simple : au chapitre 11, ce menu recevra un
> **panneau** venu d'une image, sans changer sa logique. Le mot `PONG`, lui, ira
> sur l'écran d'accueil.

### L'écran d'accueil (`pong/scenes/start.py`)

Comme le menu et les options reviennent à l'accueil avec « Échap », il faut une
scène `start`, même minimale pour l'instant :

```python
"""Écran d'accueil : toute touche ouvre le menu."""

import pygame

from .. import settings
from .base import Scene


class StartScene(Scene):
    """Écran-titre minimal : n'importe quelle touche ouvre le menu."""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.app.switch_scene("menu")

    def draw(self, surface):
        surface.fill((18, 6, 46))
        self.app.draw_text(surface, "PONG", self.app.font_large,
                           settings.NEON_YELLOW,
                           center=(settings.WINDOW_WIDTH // 2,
                                   settings.WINDOW_HEIGHT // 2))
```

> 💡 Au chapitre 11, cet écran deviendra une **vidéo** ; sa logique (toute touche
> ouvre le menu) ne changera pas.

### `pong/scenes/options.py`

```python
"""Écran Options : réglage de la difficulté et des points pour gagner."""

import pygame

from .. import settings, ui
from .base import Scene

_ROW_LEVEL = 0
_ROW_POINTS = 1


class OptionsScene(Scene):
    """Sous-menu de réglages, accessible depuis le menu principal."""

    def __init__(self, app):
        super().__init__(app)
        self.index = 0

    def handle_event(self, event):
        new_index = ui.navigation_index(event, self.index, len(self._rows()))
        if new_index is not None:
            self.index = new_index
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_HOME:
            self.app.switch_scene("start")
        elif event.key == pygame.K_LEFT:
            self._change(-1)
        elif event.key == pygame.K_RIGHT:
            self._change(1)
        elif (event.key in settings.KEY_VALIDATE
              or event.key in settings.KEY_PAUSE
              or event.key in settings.KEY_MENU):
            self.app.switch_scene("menu")

    def _change(self, delta):
        """Fait défiler la valeur de la ligne sélectionnée (boucle circulaire)."""
        config_now = self.app.config
        if self.index == _ROW_LEVEL:
            keys = list(settings.AI_LEVELS)
            config_now["level"] = keys[(keys.index(config_now["level"]) + delta) % len(keys)]
        elif self.index == _ROW_POINTS:
            choices = settings.POINT_CHOICES
            current = choices.index(config_now["points_to_win"])
            config_now["points_to_win"] = choices[(current + delta) % len(choices)]
        else:
            return

    def _rows(self):
        """Libellé et valeur affichés pour chaque ligne."""
        level = settings.AI_LEVELS[self.app.config["level"]]["label"]
        return [
            ("Difficulté", level),
            ("Points pour gagner", str(self.app.config["points_to_win"])),
            ("Retour", ""),
        ]

    def draw(self, surface):
        surface.fill((18, 6, 46))

        for i, (label, value) in enumerate(self._rows()):
            text = f"{label} : {value}" if value else label
            prefix = "> " if i == self.index else "  "
            color = settings.NEON_PINK if i == self.index else settings.TEXT_DIM
            self.app.draw_text(surface, prefix + text, self.app.font_small, color,
                               center=(settings.WINDOW_WIDTH // 2, 200 + i * 50))

        self.app.draw_text(surface, "Flèches ←/→ : changer     Entrée : retour     Échap : accueil",
                           self.app.font_small, settings.TEXT_DIM,
                           center=(settings.WINDOW_WIDTH // 2,
                                   settings.WINDOW_HEIGHT - 30))
```

### `App` — les réglages et la scène

```python
from .scenes.options import OptionsScene
from .scenes.start import StartScene
...

        self.config = {"level": "moyen", "points_to_win": settings.POINTS_TO_WIN}
        self._scenes = {"start": StartScene, "menu": MenuScene,
                        "game": GameScene, "options": OptionsScene}
```

### `tests/test_options_scene.py` (extraits)

```python
"""Tests de l'écran Options : difficulté et points pour gagner."""

import pygame

from pong import settings
from pong.app import App
from pong.scenes.menu import MenuScene
from pong.scenes.options import OptionsScene


def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


def test_options_changes_difficulty_in_config():
    app = App(sound_enabled=False)
    app.switch_scene("options")
    scene = app.scene
    scene.index = 0  # ligne « Difficulté »
    before = app.config["level"]

    scene.handle_event(_key(pygame.K_RIGHT))

    assert app.config["level"] != before
    assert app.config["level"] in settings.AI_LEVELS


def test_options_changes_points_in_config():
    app = App(sound_enabled=False)
    app.switch_scene("options")
    scene = app.scene
    scene.index = 1  # ligne « Points pour gagner »
    before = app.config["points_to_win"]

    scene.handle_event(_key(pygame.K_RIGHT))

    assert app.config["points_to_win"] != before
    assert app.config["points_to_win"] in settings.POINT_CHOICES


def test_options_return_row_goes_back_to_menu():
    app = App(sound_enabled=False)
    app.switch_scene("options")
    scene = app.scene
    scene.index = 2  # « Retour »

    scene.handle_event(_key(pygame.K_RETURN))

    assert isinstance(app.scene, MenuScene)
```

> 💡 Notre `App` prend maintenant un paramètre `sound_enabled` (chapitre 09) : les
> tests le passent à `False` pour rester silencieux. Vous pouvez aussi ajouter dès
> maintenant un paramètre `sound_enabled=True` dans `App.__init__` sans l'utiliser.

Vous avez un vrai parcours : menu → partie → menu, options → partie réglée.
Le jeu commence à ressembler à un jeu.

> **Dans le projet de référence :** `pong/ui.py` grandira au chapitre 11 (panneau,
> choix, invite) ; `pong/scenes/menu.py` et `pong/scenes/options.py` y adopteront le
> panneau par images, sans que leur logique change.

## En résumé

- Un menu se décrit par une **liste de données** (libellé, scène, paramètres).
- Le **modulo** gère le bouclage, dans les deux sens.
- Renvoyer `None` plutôt qu'une valeur sentinelle rend `navigation_index` réutilisable.
- `**kwargs` transmet les paramètres d'une scène à l'autre.
- Les réglages vivent dans `app.config` (la **persistance** viendra au chapitre 12).

## Étape suivante

→ [09 — Les sons et la pause](09-sons-et-pause.md)
