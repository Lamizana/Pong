# 08 — Le menu et les scènes

Le jeu a maintenant plusieurs écrans. Ce chapitre montre comment les faire
communiquer proprement, en commençant par le menu principal.

## Le menu

`MenuScene` présente une liste d'options et une sélection courante :

```python
class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.options = [
            ("1 joueur — Facile", "game", {"mode": "1p", "level": "facile"}),
            ("1 joueur — Moyen", "game", {"mode": "1p", "level": "moyen"}),
            ("1 joueur — Difficile", "game", {"mode": "1p", "level": "difficile"}),
            ("2 joueurs", "game", {"mode": "2p"}),
            ("Quitter", None, None),
        ]
        self.index = 0
```

Chaque option est un triplet :

1. le **libellé** affiché,
2. le **nom de la scène** à activer (`"game"`, ou `None` pour quitter),
3. les **arguments** à passer à cette scène.

Ainsi, ajouter un mode de jeu ne demande qu'une ligne dans cette liste.

## Naviguer

On réagit aux flèches **et** à Z/S, et l'on boucle aux extrémités grâce au modulo :

```python
def handle_event(self, event):
    if event.type != pygame.KEYDOWN:
        return
    if event.key in settings.P1_UP or event.key in settings.P2_UP:
        self.index = (self.index - 1) % len(self.options)
    elif event.key in settings.P1_DOWN or event.key in settings.P2_DOWN:
        self.index = (self.index + 1) % len(self.options)
    elif event.key in settings.KEY_VALIDATE:
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

`**kwargs` « déballe » le dictionnaire : `switch_scene("game", mode="1p", level="moyen")`.
Ces arguments arrivent directement au constructeur de `GameScene`.

## Le gestionnaire de scènes

Rappel de `app.py` :

```python
self._scenes = {"menu": MenuScene, "game": GameScene}

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

- `switch_scene` crée un **nouvel** écran (menu → partie, partie → fin).
- `set_scene` réactive un écran **existant** (pause → reprise de la *même* partie).

Cette distinction est ce qui permet à la pause de reprendre la partie exactement où
elle s'était arrêtée (chapitre 10).

## Dessiner le menu

```python
def draw(self, surface):
    surface.fill(settings.BLACK)
    center_x = settings.WINDOW_WIDTH // 2
    self.app.draw_text(surface, settings.CAPTION.upper(), self.app.font_large,
                       settings.ACCENT, center=(center_x, 120))
    for i, (label, _, _) in enumerate(self.options):
        selected = i == self.index
        color = settings.WHITE if selected else settings.GRAY
        prefix = "> " if selected else "  "
        self.app.draw_text(surface, prefix + label, self.app.font_medium, color,
                           center=(center_x, 240 + i * 60))
```

L'option sélectionnée est en blanc et précédée d'un `>`, les autres sont grisées.
Le `240 + i * 60` espace les lignes de 60 pixels, une technique simple pour aligner
une liste verticalement.

## Étape suivante

→ [09 — Les sons](09-les-sons.md)
