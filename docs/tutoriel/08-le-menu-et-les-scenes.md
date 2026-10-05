# 08 — Le menu et les scènes

Le jeu a maintenant plusieurs écrans. Ce chapitre montre comment les faire
communiquer proprement, en commençant par le menu principal.

## Le menu

`MenuScene` présente une liste d'options et une sélection courante :

```python
class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        # La difficulté et les points se règlent dans le sous-menu Options.
        self.options = [
            ("1 joueur", "game", {"mode": "1p"}),
            ("2 joueurs", "game", {"mode": "2p"}),
            ("Options", "options", {}),
            ("Quitter", None, None),
        ]
        self.index = 0
        self.frame = ui.fit_menu_frame(app.assets.menu_frame)
```

Chaque option est un triplet :

1. le **libellé** affiché,
2. le **nom de la scène** à activer (`"game"`, ou `None` pour quitter),
3. les **arguments** à passer à cette scène.

Ainsi, ajouter un mode de jeu ne demande qu'une ligne dans cette liste.

## Naviguer

On réagit aux flèches **et** à Z/S, et l'on boucle aux extrémités grâce au modulo.
Cette navigation est partagée par les trois écrans à panneau (menu, options, fin) via
`pong/ui.py` :

```python
def navigation_index(event, index, count):
    if event.type != pygame.KEYDOWN:
        return None
    if event.key in settings.P1_UP or event.key in settings.P2_UP:
        return (index - 1) % count
    if event.key in settings.P1_DOWN or event.key in settings.P2_DOWN:
        return (index + 1) % count
    return None
```

La scène s'en sert simplement :

```python
def handle_event(self, event):
    new_index = ui.navigation_index(event, self.index, len(self.options))
    if new_index is not None:
        self.index = new_index
    elif event.type == pygame.KEYDOWN and event.key in settings.KEY_VALIDATE:
        self._select()
```

`(self.index - 1) % len(...)` : en Python, `-1 % 5` vaut `4`. Le modulo fait
naturellement « revenir » en bas de la liste quand on va trop haut, et inversement.

## Activer une scène

```python
def _select(self):
    _, scene_name, kwargs = self.options[self.index]
    if scene_name is None:
        self.app.quit()
    else:
        self.app.switch_scene(scene_name, **kwargs)
```

`**kwargs` « déballe » le dictionnaire : `switch_scene("game", mode="1p")`.
Ces arguments arrivent directement au constructeur de `GameScene`.

## Le gestionnaire de scènes

Rappel de `app.py` :

```python
self._scenes = {"menu": MenuScene, "game": GameScene, "options": OptionsScene}

def switch_scene(self, name, **kwargs):
    self.scene = self._scenes[name](self, **kwargs)
```

Le dictionnaire associe un nom à une **classe**, pas à une instance. On construit
donc une scène neuve à chaque fois — un menu ne « garde » aucun état entre deux
visites, ce qui est exactement ce qu'on veut.

## Enchaîner les écrans

Le cycle complet d'une session :

```
         ┌──────────┐
         │   Menu   │◄──────────────────────┐
         └────┬─────┘                        │
              │ Entrée (mode choisi)         │
              ▼                              │
         ┌──────────┐   P / Échap   ┌──────┐ │ Q
         │  Partie  │◄─────────────►│Pause │─┘
         └────┬─────┘   P / Entrée  └──────┘
              │ quelqu'un atteint N points
              ▼
         ┌──────────┐
         │ Fin      │ Entrée : rejouer  → Partie
         │(vainqueur)│ M ou Q : menu
         └──────────┘
```

- `switch_scene` crée un **nouvel** écran (menu → partie, fin → rejouer).
- `set_scene` réactive un écran **existant** (pause → reprise de la *même* partie,
  partie → écran de fin, construite explicitement).

Cette distinction est ce qui permet à la pause de reprendre la partie exactement où
elle s'était arrêtée (chapitre 10).

## Dessiner le menu

```python
def draw(self, surface):
    surface.blit(self.app.assets.menu_background, (0, 0))
    frame_rect = ui.panel_rect(self.frame)
    surface.blit(self.frame, frame_rect)

    title = self.app.assets.title
    surface.blit(title, title.get_rect(center=(
        settings.WINDOW_WIDTH // 2, frame_rect.top + 8 + title.get_height() // 2)))

    ui.draw_choices(surface, self.app, frame_rect,
                    [label for label, _, _ in self.options], self.index)
    ui.draw_hint(surface, self.app,
                 "Flèches ou Z/S : naviguer     Entrée : valider")
```

L'option sélectionnée est en **rose néon** et précédée d'un `>`, les autres en gris
clair. `ui.draw_choices` répartit les lignes dans la zone centrale du panneau, et
`ui.draw_hint` affiche l'invite en bas de la fenêtre.

> **Note** : les chapitres précédents restent volontairement sur un fond **noir uni**,
> pour se concentrer sur la mécanique. C'est le [chapitre 12](12-theme-et-assets.md)
> qui habille le jeu (images, police), sans toucher à la logique.

## Étape suivante

→ [09 — Les sons](09-les-sons.md)

> Pour le style visuel final (thème cyberpunk à base d'images), voir le
> [chapitre 12](12-theme-et-assets.md).
