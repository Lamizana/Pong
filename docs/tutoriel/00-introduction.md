# 00 — Introduction

## Le jeu

Le **Pong** est l'un des tout premiers jeux vidéo (1972). Deux raquettes verticales
se font face, de part et d'autre de l'écran, et une balle rebondit entre elles.
Un joueur marque un point quand la balle sort derrière la raquette adverse.

C'est un excellent premier projet de jeu : les règles sont simples, mais on y
retrouve tous les ingrédients d'un vrai jeu — une boucle, des entités qui bougent,
des collisions, une IA, un score, des menus et du son.

## Ce que ce projet couvre

| Fonctionnalité | Chapitre |
|----------------|----------|
| Fenêtre, boucle de jeu, scènes | 03 |
| Raquettes et contrôle clavier | 04 |
| Balle, collisions, rebonds | 05 |
| IA à trois niveaux de difficulté | 06 |
| Score et condition de victoire | 07 |
| Menu, pause, fin de partie | 08, 10 |
| Sons générés en code | 09 |
| Exécutables Linux / Windows | 11 |

## Architecture générale

Le programme est organisé en couches. De bas en haut :

```
┌───────────────────────────────────────────────┐
│  main.py            (point d'entrée)           │
├───────────────────────────────────────────────┤
│  pong/app.py        (fenêtre, boucle, scènes)  │
├───────────────────────────────────────────────┤
│  pong/scenes/       menu, game, pause, gameover│
├───────────────────────────────────────────────┤
│  pong/ball.py  paddle.py  ai.py  score.py      │  ← logique du jeu (testée)
├───────────────────────────────────────────────┤
│  pong/settings.py   (constantes)               │
└───────────────────────────────────────────────┘
```

- **`settings.py`** rassemble toutes les valeurs réglables (taille de l'écran,
  couleurs, vitesses, touches). On ne les disperse pas dans le code.
- **`ball`, `paddle`, `ai`, `score`** contiennent les *règles* du jeu. Ils ne
  dessinent rien et ne dépendent pas de la boucle : on peut les tester isolément.
- **`scenes/`** contient les *écrans* : le menu, la partie, la pause, la fin.
- **`app.py`** orchestre le tout : il ouvre la fenêtre, lit le clavier et confie
  le travail à la scène courante.

Cette séparation est le fil rouge du tutoriel. Elle paraît un peu formelle au début,
mais tu verras qu'elle rend chaque chapitre très lisible : on parle d'un fichier à
la fois.

## Comment lire ce tutoriel

Chaque chapitre de code suit le même schéma :

1. **Le problème** : qu'est-ce qu'on cherche à faire ?
2. **Le test** : qu'attend-on, concrètement ? (on écrit le test d'abord)
3. **L'implémentation** : le code qui satisfait le test.
4. **L'explication** : les concepts pygame/Python derrière le code.

Tu peux suivre le projet d'un bout à l'autre en tapant le code, ou simplement lire
et exécuter le projet déjà terminé. Chaque chapitre indique où il se situe dans
l'arborescence finale.

## Étape suivante

→ [01 — Installation](01-installation.md)
