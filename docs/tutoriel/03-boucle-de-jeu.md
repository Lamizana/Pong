# 03 — La boucle de jeu

Tout jeu vidéo repose sur une **boucle** qui tourne des dizaines de fois par
seconde : lire les entrées, mettre à jour le monde, redessiner l'écran, recommencer.
C'est le cœur de notre `App`.

## Le point d'entrée

`main.py` ne fait presque rien : il crée l'application et la lance.

```python
from pong.app import App


def main():
    App().run()


if __name__ == "__main__":
    main()
```

La condition `if __name__ == "__main__":` garantit que `main()` n'est exécuté que
si l'on lance le fichier directement (`python main.py`), et pas si on l'importe
depuis un test.

## Initialiser pygame

Créer une fenêtre avec pygame tient en quelques lignes :

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((900, 600))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()
```

- `pygame.init()` démarre les sous-systèmes (affichage, son, polices).
- `set_mode((largeur, hauteur))` ouvre la fenêtre et renvoie sa **surface** :
  la zone de pixels sur laquelle on dessine.
- `Clock` servira à cadrer le nombre d'images par seconde.

## La boucle principale

Voici la boucle de `pong/app.py`, simplifiée :

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

Décortiquons-la.

### `clock.tick(FPS)`

`tick(60)` attend le temps nécessaire pour ne pas dépasser 60 images par seconde,
et renvoie le nombre de **millisecondes** écoulées depuis l'image précédente. En le
divisant par 1000, on obtient `dt`, le **delta time** en secondes.

### Pourquoi `dt` ?

Imagine que la balle avance de « 5 pixels par image ». Sur un écran à 144 Hz, elle
ira presque trois fois plus vite que sur un écran à 60 Hz ! Pour éviter cela, on
exprime les vitesses en **pixels par seconde** et on les multiplie par `dt` :

```python
self.x += self.vx * dt
```

Ainsi, quel que soit le matériel, la balle parcourt la même distance en une seconde.

Le `min(dt, 0.05)` plafonne `dt` à 50 ms : si le système se met en pause (fenêtre
réduite, machine occupée), on évite que la balle ne « saute » à travers les murs au
retour.

### La file d'événements

`pygame.event.get()` renvoie tout ce qui s'est passé depuis l'image précédente :
touches pressées, clic sur la croix, etc. On traite en priorité `QUIT` (fermeture
de fenêtre), puis on délègue le reste à la scène.

Note la structure `for ... else` : le `else` ne s'exécute que si la boucle `for` n'a
pas été interrompue par le `break`. Autrement dit, si on vient de fermer la fenêtre,
on **saute** la mise à jour et le dessin de cette image.

### Dessiner

`pygame.display.flip()` est indispensable : c'est lui qui rend visible ce qu'on vient
de dessiner. Sans appel à `flip()`, l'écran reste figé.

Le `try ... finally: pygame.quit()` garantit que pygame est fermé proprement, même si
une erreur survient. Et la variable locale `scene` « fige » la scène du début d'image :
si un événement déclenche un changement de scène, les événements restants de la même
image ne sont pas envoyés par erreur à la nouvelle scène.

## Les scènes

Un jeu a plusieurs écrans : menu, partie, pause, fin de partie. Plutôt qu'un gros
`if` pour savoir lequel afficher, on utilise des **scènes**. Chaque scène est un
objet avec trois méthodes, décrites dans `pong/scenes/base.py` :

```python
class Scene:
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        """Réagit à un événement pygame."""

    def update(self, dt):
        """Met à jour la logique de la scène."""

    def draw(self, surface):
        """Dessine la scène."""
```

- `handle_event` : traiter une touche ou un clic.
- `update` : faire avancer la logique (déplacer la balle...).
- `draw` : dessiner l'écran.

L'`App` ne connaît que **la** scène courante et lui délègue tout :

```python
def switch_scene(self, name, **kwargs):
    self.scene = self._scenes[name](self, **kwargs)

def set_scene(self, scene):
    self.scene = scene
```

- `switch_scene` construit une **nouvelle** scène (par exemple depuis le menu vers
  la partie).
- `set_scene` réactive une scène **déjà existante** : utile pour reprendre une partie
  mise en pause, sans la recréer.

## Et les polices ?

Pour afficher du texte, on charge des polices dans `App.__init__` :

```python
self.font_small = pygame.font.SysFont(None, 28)
self.font_medium = pygame.font.SysFont(None, 44)
self.font_large = pygame.font.SysFont(None, 72)
```

`SysFont(None, taille)` utilise la police système par défaut : aucune ressource à
embarquer. Un petit utilitaire centralise le rendu :

```python
def draw_text(self, surface, text, font, color, center=None, topleft=None):
    image = font.render(text, True, color)
    rect = image.get_rect()
    if center is not None:
        rect.center = center
    if topleft is not None:
        rect.topleft = topleft
    surface.blit(image, rect)
    return rect
```

## Vérification

À ce stade, la fenêtre s'ouvre sur un écran noir qui se ferme proprement. C'est peu,
mais toute la mécanique est là. Le [test de fumée](../../tests/test_app_smoke.py)
vérifie d'ailleurs que ce squelette fonctionne sans écran réel.

## Étape suivante

→ [04 — Les raquettes](04-les-raquettes.md)
