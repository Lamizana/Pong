# 10 — La fin de partie

## Objectifs

À la fin de ce chapitre, vous saurez :

- créer un **écran de fin** dédié, avec les bonnes informations ;
- réutiliser la **navigation** d'un menu dans une autre scène ;
- relancer une partie **dans le mode choisi** ;
- enchaîner les scènes proprement : partie → fin → partie / menu.

**Fichiers du projet :** `pong/scenes/gameover.py`, `pong/scenes/game.py`
**Test du projet :** `tests/test_gameover_scene.py`

## 1. Un écran dédié

Quand un joueur atteint le nombre de points, la partie doit s'arrêter et **dire
pourquoi**. On ne dessine pas un message par-dessus la partie : on bascule vers une
scène dédiée. C'est plus clair, et surtout **testable**.

```python
class GameOverScene(Scene):
    """Menu de fin : « Rejouer » (même mode) ou « Menu »."""

    def __init__(self, app, winner, mode):
        super().__init__(app)
        self.winner = winner          # "left" ou "right"
        self.mode = mode              # "1p" ou "2p"
        self.options = [("Rejouer", "replay"), ("Menu", "menu")]
        self.index = 0
```

On lui transmet **deux informations** :

- `winner` : qui a gagné ;
- `mode` : dans quel mode la partie se jouait — indispensable pour rejouer **à
  l'identique**.

## 2. Le bon message

Trois cas à distinguer, car il n'y a pas toujours deux joueurs :

```python
        if self.winner == "left":
            title = "Victoire du joueur 1 !"
            color = settings.NEON_CYAN
        elif self.mode == "1p":
            title = "Victoire de l'IA !"
            color = settings.NEON_PINK
        else:
            title = "Victoire du joueur 2 !"
            color = settings.NEON_PINK
```

- « gauche » gagne → c'est **toujours** le joueur 1 (il contrôle la raquette de
  gauche, quel que soit le mode) ;
- « droite » gagne en 1 joueur → c'est **l'IA** ;
- « droite » gagne en 2 joueurs → c'est le **joueur 2**.

## 3. Un menu de fin navigable

Plutôt que deux raccourcis clavier, on offre un **vrai menu** à deux entrées,
navigable au clavier comme le menu principal :

```
        Victoire du joueur 1 !

        > Rejouer
          Menu
```

On réutilise le helper du chapitre 08 — et c'est tout l'intérêt de l'avoir isolé :

```python
    def handle_event(self, event):
        new_index = ui.navigation_index(event, self.index, len(self.options))
        if new_index is not None:
            self.index = new_index
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_HOME:
            self.app.switch_scene("start")
        elif event.key in settings.KEY_VALIDATE:
            self._select()
        elif event.key in settings.KEY_MENU:
            self.app.switch_scene("menu")
```

Et l'action :

```python
    def _select(self):
        action = self.options[self.index][1]
        if action == "replay":
            self.app.switch_scene("game", mode=self.mode)
        else:
            self.app.switch_scene("menu")
```

> 💡 On stocke une **action** (`"replay"` / `"menu"`), pas une scène : « Rejouer »
> n'est pas un écran, c'est un comportement qui dépend du mode. Cette petite
> indirection garde le menu déclaratif.

## 4. Le lien depuis la partie

Dans `GameScene`, au moment où le score désigne un vainqueur :

```python
        winner = self.score.add_point(scorer)
        if winner is not None:
            self.app.sound.win()
            self.app.set_scene(GameOverScene(self.app, winner, self.mode))
            return
```

On utilise `set_scene` (et non `switch_scene`) car il n'y a **rien à construire via
le dictionnaire** : on fabrique la scène nous-mêmes, avec ses paramètres.

## À vous de jouer !

1. Écrivez `pong/scenes/gameover.py`.
2. Écrivez les tests (`tests/test_gameover_scene.py`) :
   - les flèches haut/bas déplacent la sélection (et bouclent) ;
   - Entrée sur « Rejouer » relance une partie **dans le même mode** ;
   - Entrée sur « Menu » revient au menu ;
   - `Q`/`M` revient directement au menu ;
   - `draw` ne lève pas d'erreur.
3. Branchez la victoire dans `GameScene` (son de victoire + bascule).
4. **Vérifiez à la main** : jouez une partie en 1 joueur à 3 points, perdez, puis
   choisissez « Rejouer » : vous devez repartir en 1 joueur, à 3 points.

<details>
<summary>Un indice pour les tests</summary>

Un test n'a pas besoin de « jouer » une partie : on peut placer directement une
scène de fin.

```python
app.set_scene(GameOverScene(app, "left", "1p"))
scene = app.scene
scene.handle_event(_key(pygame.K_DOWN))
assert scene.index == 1
```

</details>

## Corrigé

### `pong/scenes/gameover.py`

```python
"""Écran de fin de partie : annonce le vainqueur et propose de rejouer."""

import pygame

from .. import settings, ui
from .base import Scene


class GameOverScene(Scene):
    """Menu de fin : « Rejouer » (relance dans le même mode) ou « Menu »."""

    def __init__(self, app, winner, mode):
        super().__init__(app)
        self.winner = winner
        self.mode = mode
        self.options = [("Rejouer", "replay"), ("Menu", "menu")]
        self.index = 0

    def handle_event(self, event):
        new_index = ui.navigation_index(event, self.index, len(self.options))
        if new_index is not None:
            self.index = new_index
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_HOME:
            self.app.switch_scene("start")
        elif event.key in settings.KEY_VALIDATE:
            self._select()
        elif event.key in settings.KEY_MENU:
            self.app.switch_scene("menu")

    def _select(self):
        action = self.options[self.index][1]
        if action == "replay":
            self.app.switch_scene("game", mode=self.mode)
        else:
            self.app.switch_scene("menu")

    def draw(self, surface):
        surface.fill((18, 6, 46))
        center_x = settings.WINDOW_WIDTH // 2

        if self.winner == "left":
            title = "Victoire du joueur 1 !"
            color = settings.NEON_CYAN
        elif self.mode == "1p":
            title = "Victoire de l'IA !"
            color = settings.NEON_PINK
        else:
            title = "Victoire du joueur 2 !"
            color = settings.NEON_PINK

        self.app.draw_text(surface, title, self.app.font_medium, color,
                           center=(center_x, 230))

        for i, (label, _) in enumerate(self.options):
            prefix = "> " if i == self.index else "  "
            text_color = settings.NEON_PINK if i == self.index else settings.TEXT_DIM
            self.app.draw_text(surface, prefix + label, self.app.font_small,
                               text_color, center=(center_x, 330 + i * 40))

        self.app.draw_text(surface, "↑/↓ ou Z/S : choisir     Entrée : valider     Échap : accueil",
                           self.app.font_small, settings.TEXT_DIM,
                           center=(center_x, settings.WINDOW_HEIGHT - 30))
```

### `tests/test_gameover_scene.py`

```python
"""Tests de l'écran de fin de partie : menu Rejouer / Menu navigable."""

import pygame

from pong.app import App
from pong.scenes.game import GameScene
from pong.scenes.gameover import GameOverScene
from pong.scenes.menu import MenuScene
from pong.scenes.start import StartScene


def _key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


def _game_over(app):
    """Place une scène de fin de partie (victoire joueur 1, mode 1 joueur)."""
    app.set_scene(GameOverScene(app, "left", "1p"))
    return app.scene


def test_arrow_keys_move_selection():
    app = App(sound_enabled=False)
    scene = _game_over(app)

    scene.handle_event(_key(pygame.K_DOWN))
    assert scene.index == 1
    scene.handle_event(_key(pygame.K_UP))
    assert scene.index == 0


def test_validate_replay_restarts_in_same_mode():
    app = App(sound_enabled=False)
    scene = _game_over(app)
    assert scene.index == 0  # « Rejouer »

    scene.handle_event(_key(pygame.K_RETURN))

    assert isinstance(app.scene, GameScene)
    assert app.scene.mode == "1p"


def test_validate_menu_returns_to_menu():
    app = App(sound_enabled=False)
    scene = _game_over(app)
    scene.handle_event(_key(pygame.K_DOWN))  # « Menu »

    scene.handle_event(_key(pygame.K_RETURN))

    assert isinstance(app.scene, MenuScene)


def test_menu_key_returns_to_menu():
    app = App(sound_enabled=False)
    scene = _game_over(app)

    scene.handle_event(_key(pygame.K_m))

    assert isinstance(app.scene, MenuScene)


def test_escape_returns_to_home_screen():
    app = App(sound_enabled=False)
    scene = _game_over(app)

    scene.handle_event(_key(pygame.K_ESCAPE))

    assert isinstance(app.scene, StartScene)
```

> 💡 Ces tests n'ouvrent aucune fenêtre : ils **simulent** des événements clavier et
> vérifient l'état de l'application. C'est rapide et fiable.

### Le lien dans `GameScene`

```python
from .gameover import GameOverScene
...

    def _handle_score(self):
        side = self.ball.off_screen()
        if side is None:
            return

        scorer = "right" if side == "left" else "left"
        winner = self.score.add_point(scorer)
        self.app.sound.point_scored()

        if winner is not None:
            self.app.sound.win()
            self.app.set_scene(GameOverScene(self.app, winner, self.mode))
            return

        self.serve_direction = 1 if scorer == "left" else -1
        self.serve_timer = 1.0
        self.ball.reset(direction=self.serve_direction)
        self.left_paddle.reset()
        self.right_paddle.reset()
        if self.ai is not None:
            self.ai.randomize_offset()
```

Bravo : le jeu est **complet**. Menu, options, partie (1 ou 2 joueurs), IA, score,
sons, pause et fin de partie : tout y est.

> **Dans le projet de référence :** `pong/scenes/gameover.py` recevra au chapitre 11
> le panneau par images. Ses tests sont ceux de ce corrigé, rejoints par un test
> d'affichage sans erreur.

## En résumé

- Un état de jeu mérite **sa propre scène** : plus clair, et testable.
- On transmet les **données nécessaires** (`winner`, `mode`) — rien de plus.
- Un menu de fin **réutilise** la navigation des autres menus.
- Stocker une **action** plutôt qu'une scène garde le menu déclaratif.
- `set_scene` quand on construit la scène soi-même, `switch_scene` quand c'est le
  dictionnaire qui la fabrique.

## Étape suivante

→ [11 — Le thème par images](11-le-theme-par-images.md)
