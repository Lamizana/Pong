# Tutoriel — Créer un jeu Pong en Python

Bienvenue ! Ce tutoriel t'accompagne de zéro jusqu'à un jeu **Pong** complet et
déployable, écrit en **Python** avec la bibliothèque **pygame**.

![Aperçu du jeu](../screenshots/game.png)

Il ne se contente pas de montrer « quel code taper » : à chaque étape, on explique
**pourquoi** on écrit ce code, quels concepts sont en jeu, et comment vérifier que
tout fonctionne grâce aux **tests**.

## Ce que tu vas construire

- Un jeu Pong jouable à **1 joueur** (contre une IA à 3 niveaux) ou à **2 joueurs**.
- Un **menu** de sélection du mode.
- Un **score** avec condition de victoire.
- Une **physique de rebond** qui dépend du point d'impact sur la raquette.
- Des **sons** générés en code (aucun fichier audio).
- Une **pause**.
- Des **exécutables** Linux et Windows (via PyInstaller et GitHub Actions).
- Un **thème cyberpunk** à base d'images générées par IA : décor néon, raquettes
  mécaniques, panneau de menu, et une **police** dédiée.

## Prérequis

- Savoir écrire un peu de Python (variables, fonctions, classes).
- Aucune connaissance préalable de pygame n'est nécessaire.

## Parcours conseillé

Lis les chapitres dans l'ordre. Chacun s'appuie sur le précédent.

| # | Chapitre | Ce qu'on y apprend |
|---|----------|--------------------|
| 00 | [Introduction](00-introduction.md) | Vue d'ensemble et architecture |
| 01 | [Installation](01-installation.md) | Mettre en place l'environnement |
| 02 | [Structure du projet](02-structure-du-projet.md) | Organiser le code en modules |
| 03 | [La boucle de jeu](03-boucle-de-jeu.md) | Fenêtre, événements, scènes |
| 04 | [Les raquettes](04-les-raquettes.md) | Entités, déplacement, bornes |
| 05 | [La balle et la physique](05-la-balle-et-la-physique.md) | Vecteurs, rebonds, angles |
| 06 | [L'IA](06-lia.md) | Un adversaire automatique battable |
| 07 | [Le score et la victoire](07-score-et-victoire.md) | Règles du jeu |
| 08 | [Le menu et les scènes](08-le-menu-et-les-scenes.md) | Navigation entre écrans |
| 09 | [Les sons](09-les-sons.md) | Générer du son sans fichier |
| 10 | [La pause](10-la-pause.md) | Figer et reprendre une partie |
| 11 | [Packaging et déploiement](11-packaging-deploiement.md) | Créer les exécutables |
| 12 | [Le thème : images et police](12-theme-et-assets.md) | Habiller le jeu (assets, police, halos néon) |

## Philosophie du projet

Ce projet est construit selon trois principes qui reviennent dans chaque chapitre :

1. **Une seule responsabilité par fichier.** La balle s'occupe de la balle, le score
   du score, les scènes de l'affichage. C'est plus facile à comprendre, à tester et
   à faire évoluer.
2. **Séparer la logique de l'affichage.** Les règles du jeu (physique, IA, score) ne
   dépendent pas de pygame : on peut les tester sans ouvrir de fenêtre.
3. **Le développement piloté par les tests (TDD).** Pour chaque brique de logique, on
   écrit d'abord un test qui échoue, puis on écrit le code qui le fait passer au vert.

Bon voyage, et amuse-toi bien ! 🏓
