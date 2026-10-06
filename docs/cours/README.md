# Créer un jeu Pong en Python avec pygame

---

Bienvenue ! Ce cours vous apprend à construire **de A à Z** un jeu **Pong** complet en **Python** avec **pygame** : de l'architecture au code, en passant par les tests.

À la fin du cours, vous aurez un jeu jouable à 1 ou 2 joueurs, avec une IA à trois niveaux, un menu, des options, des sons, une pause, un écran de fin, des tests automatisés, et un habillage « néon » à base d'images.

> [!Note]
> **Vous allez écrire le code vous-même.**
> - Chaque chapitre se termine par un exercice « ***À vous de jouer !*** », suivi de son corrigé complet.

---

## Prérequis

- Savoir écrire un peu de Python : variables, conditions, boucles, fonctions, classes.
- Aucune connaissance de pygame n'est nécessaire.
- Un ordinateur sous Linux, macOS ou Windows, avec **Python 3.10** ou plus récent.

---

## Comment suivre ce cours

Chaque chapitre suit le même déroulé :

1. **Objectifs** : ce que vous saurez faire à la fin du chapitre.
2. **Théorie** : les concepts, expliqués simplement (avec schémas et tableaux).
3. **À vous de jouer !** : Un exercice : c'est **vous** qui écrivez le code, et le **test d'abord**.
4. **Corrigé** : La solution complète, expliquée ligne à ligne.
5. **En résumé** :  L'essentiel à retenir.

Le corrigé est **autonome** :

- vous pouvez suivre tout le cours sans le dépôt du projet.
- Chaque chapitre indique aussi le **fichier** et le **test** correspondants, si vous voulez comparer avec l'implémentation de référence.

---

## Les 4 parties

| Partie | Ce que vous construisez | Chapitres |
|--------|-------------------------|-----------|
| **1. Les fondations** | L'environnement, la boucle de jeu, les scènes | 00 → 02 |
| **2. La logique du jeu** | Les raquettes, la balle, les collisions, l'IA, le score | 03 → 07 |
| **3. Les écrans** | Le menu, les options, les sons, la pause, la fin de partie | 08 → 10 |
| **4. L'habillage** | Le thème par images, le polish et le déploiement | 11 → 12 |

## Table des chapitres

| # | Chapitre | Ce que vous y apprenez |
|---|----------|------------------------|
| *00* | [Introduction et architecture](00-introduction.md) | Le jeu, l'architecture du projet, le TDD |
| *01* | [L'environnement](01-environnement.md) | venv, pygame, pytest, première fenêtre |
| *02* | [La boucle et les scènes](02-boucle-et-scenes.md) | `App`, delta time, `Scene`, constantes |
| *03* | [Les raquettes](03-les-raquettes.md) | Une entité qui bouge et qui a des bornes |
| *04* | [La balle](04-la-balle.md) | Vecteurs, rebonds, delta time |
| *05* | [Les collisions](05-les-collisions.md) | Cercle contre rectangle, le cas du coin |
| *06* | [L'IA](06-lia.md) | Un adversaire automatique battable |
| *07* | [Le score et la victoire](07-le-score.md) | Les règles du jeu |
| *08* | [Le menu et les options](08-le-menu-et-les-options.md) | Naviguer entre écrans, régler le jeu |
| *09* | [Les sons et la pause](09-sons-et-pause.md) | Générer du son sans fichier |
| *10* | [La fin de partie](10-la-fin-de-partie.md) | Un menu de fin navigable |
| *11* | [Le thème par images](11-le-theme-par-images.md) | Charger des sprites, détourer un fond |
| *12* | [Le polish et le déploiement](12-polish-et-deploiement.md) | Police, halos, réglages, exécutables |

---

## Les 3 principes du projet

Ils reviennent dans chaque chapitre :

1. **Une responsabilité par fichier.** La balle s'occupe de la balle, le score du score, les scènes de l'affichage. C'est plus simple à comprendre, à tester et à faire évoluer.
2. **Séparer la logique de l'affichage.** Les règles du jeu (physique, IA, score) ne dépendent pas de l'affichage : on peut les tester sans ouvrir de fenêtre.
3. **Développer par les tests (TDD).** Pour chaque brique de logique : un test qui échoue, puis le code qui le fait passer au vert.

Bonne route, et amusez-vous bien ! 🏓

---

**Premier chapitre : [00. Introduction et architecture >>>](00-introduction.md)**
