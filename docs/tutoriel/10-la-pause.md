# 10 — La pause

Une pause bien faite ne se contente pas de figer la balle : elle affiche un message
clair et permet de **reprendre exactement où l'on s'était arrêté**. C'est un bon
exercice sur la distinction entre `switch_scene` et `set_scene`.

## L'idée : ne pas recréer la partie

Souviens-toi du [chapitre 08](08-le-menu-et-les-scenes.md) :

- `switch_scene("game", ...)` **construit une nouvelle partie** (scores à zéro).
- `set_scene(scene)` réactive un **objet existant**, avec son état intact.

Pour la pause, on garde donc une **référence** à la partie en cours :

```python
class GameScene(Scene):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in settings.KEY_PAUSE:
            self.app.set_scene(PauseScene(self.app, self))
```

On passe `self` (la partie) à la pause. Comme il s'agit du **même objet** en mémoire,
ses scores, positions et minuteurs sont conservés : on n'a rien à sauvegarder ni à
restaurer.

## La scène de pause

```python
class PauseScene(Scene):
    def __init__(self, app, game):
        super().__init__(app)
        self.game = game

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in settings.KEY_PAUSE or event.key in settings.KEY_VALIDATE:
            self.app.set_scene(self.game)          # reprendre la même partie
        elif event.key == pygame.K_q:
            self.app.switch_scene("menu")          # abandonner et revenir au menu

    def draw(self, surface):
        self.game.draw(surface)                    # la partie reste visible, figée
        ...
```

Deux points essentiels :

1. `update` n'est **pas** redéfini : la classe de base `Scene` ne fait rien. La partie
   n'avance donc pas tant qu'on est en pause.
2. On appelle `self.game.draw(surface)` pour dessiner la partie en arrière-plan : on
   voit l'état du jeu derrière le message.

## L'overlay semi-transparent

Pour assombrir l'arrière-plan, on dessine un rectangle noir semi-transparent par
dessus la partie :

```python
def draw(self, surface):
    self.game.draw(surface)

    overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    overlay.set_alpha(170)               # 0 = invisible, 255 = opaque
    overlay.fill(settings.BLACK)
    surface.blit(overlay, (0, 0))

    center_x = settings.WINDOW_WIDTH // 2
    self.app.draw_text(surface, "PAUSE", self.app.font_large, settings.WHITE,
                       center=(center_x, 240))
    self.app.draw_text(surface, "P ou Entrée : reprendre", self.app.font_small,
                       settings.GRAY, center=(center_x, 320))
    self.app.draw_text(surface, "Q : retour au menu", self.app.font_small,
                       settings.GRAY, center=(center_x, 350))
```

Pourquoi une surface séparée plutôt que dessiner directement en transparence ? Parce
que `set_alpha` s'applique à une **surface entière**. On crée donc une image noire,
on lui donne une opacité, puis on la colle sur l'écran.

> **Piège classique** : `set_alpha` ne fonctionne que sur des surfaces *avec canal
> alpha*. Créer la surface via `pygame.Surface((w, h))` puis appeler `set_alpha`
> fonctionne ici car on ne dessine que du noir uni. Pour des formes colorées
> superposées, on utiliserait `convert_alpha()`.

## Rejouer

Le même principe sert à l'écran de fin de partie. `GameOverScene` retient le mode et
la difficulté pour relancer une partie identique :

```python
def handle_event(self, event):
    if event.type != pygame.KEYDOWN:
        return
    if event.key in settings.KEY_VALIDATE:
        self.app.switch_scene("game", mode=self.mode, level=self.level)
    elif event.key in (pygame.K_q, pygame.K_m):
        self.app.switch_scene("menu")
```

Ici, au contraire de la pause, on veut une partie **neuve** : `switch_scene` est donc
le bon choix.

## Récapitulatif : quel appel utiliser ?

| Situation | Méthode | Pourquoi |
|-----------|---------|----------|
| Menu → partie | `switch_scene("game", ...)` | Nouvelle partie |
| Partie → pause | `set_scene(PauseScene(...))` | On fige, on garde l'état |
| Pause → partie | `set_scene(self.game)` | On reprend la **même** partie |
| Partie → fin | `set_scene(GameOverScene(...))` | Écran de résultat |
| Fin → rejouer | `switch_scene("game", ...)` | Partie neuve |
| Partie/fin/pause → menu | `switch_scene("menu")` | Menu neuf |

## Étape suivante

→ [11 — Packaging et déploiement](11-packaging-deploiement.md)
