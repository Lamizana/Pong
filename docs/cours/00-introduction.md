# Introduction et architecture

---

## Objectifs

À la fin de ce chapitre, vous saurez :

- Ce que vous allez construire, chapitre après chapitre ;
- Comment le projet est **organisé en couches**, et pourquoi cette séparation est la clé d'un code lisible ;
- Ce qu'est le **développement piloté par les tests** (TDD), qu'on appliquera partout.

---

## 1. Le jeu Pong

Le **Pong** est l'un des tout premiers jeux vidéo (1972).

Deux raquettes verticales se font face et une balle rebondit entre elles. Un joueur marque un point quand la balle passe derrière la raquette adverse.

<div align="center">
  <p>
    <img src="images/Pong.svg" alt="Pong originel" width="380">
  </p>
  <p><em>Premier Pong sortit en 1972</em></p>

</div>

```
        ┌──────────────────────────────┐
        │                              │
        │  ▍                        ▐  │
        │  ▍          ●             ▐  │
        │  ▍                        ▐  │
        │                              │
        └──────────────────────────────┘
         joueur 1              joueur 2
```

***C'est un excellent premier projet*** !

Les règles tiennent en une phrase, mais on y retrouve **tous** les ingrédients d'un vrai jeu :

- Une boucle
- Des objets qui bougent
- Des collisions
- Une IA
- Un score
- Des menus et du son.

---

## 2. Ce que vous allez construire

| Fonctionnalité | Chapitre |
|----------------|----------|
| Fenêtre, boucle de jeu, scènes | **02** |
| Raquettes et contrôle au clavier | **03** |
| Balle, rebonds, physique | **04** |
| Collisions raquette / balle | **05** |
| IA à trois niveaux de difficulté | **06** |
| Score et condition de victoire | **07** |
| Menu, options, pause, fin de partie | **08**, **09**, **10** |
| Sons générés en code | **09** |
| Thème par images et police dédiée | **11**, **12** |
| Exécutables Linux et Windows | **12** |

---

## 3. L'architecture : des couches de responsabilités

Un jeu qui tient dans un seul fichier devient vite illisible. Nous allons donc répartir le travail en **couches**, chacune avec **une responsabilité** :

```console
┌──────────────────────────────────────────────────────────────┐
│  main.py            Point d'entrée : lance l'application     │
├──────────────────────────────────────────────────────────────┤
│  pong/app.py        Fenêtre, horloge, boucle, scènes         │
├──────────────────────────────────────────────────────────────┤
│  pong/scenes/       Les ÉCRANS : menu, partie, pause…        │
│                     (ils dessinent, ils ne calculent pas)    │
├──────────────────────────────────────────────────────────────┤
│  pong/ball.py       paddle.py  ai.py  score.py  collision.py │
│                     La LOGIQUE : les règles du jeu           │
│                     (aucun dessin, 100 % testable)           │
├──────────────────────────────────────────────────────────────┤
│  pong/settings.py   Toutes les constantes réglables          │
└──────────────────────────────────────────────────────────────┘
```

Détaillons chaque couche :

- **`settings.py`** rassemble les valeurs réglables (taille de la fenêtre, couleurs, vitesses, touches). On ne les disperse pas dans le code : pour changer la vitesse de la balle, il n'y a qu'un seul endroit à modifier.
- **`ball`, `paddle`, `ai`, `score`, `collision`** contiennent les **règles** du jeu. Ils ne dessinent rien et n'ouvrent aucune fenêtre : on peut donc les tester isolément, en quelques millisecondes.
- **`scenes/`** contient les **écrans** : le menu, la partie, la pause, la fin de partie. Une scène **dessine** et **traduit les touches** en actions, mais délègue les calculs à la logique.
- **`app.py`** orchestre le tout : il ouvre la fenêtre, lit le clavier, et confie le
  travail à la **scène courante**.
- **`main.py`** ne fait presque rien : il crée l'application et la lance.

> [!Note]
> **Pourquoi cette séparation ?** Parce qu'elle rend chaque chapitre très lisible :
> - on parle d'**un fichier à la fois**. Et surtout, elle permet de tester la physique du jeu **sans ouvrir de fenêtre**,ce qui sera notre filet de sécurité.

---

## 4. Le développement piloté par les tests (TDD)

Pour toute la logique du jeu, nous suivrons un rythme en trois temps, appelé
**rouge → vert → refactor** :

```
   ① ROUGE                     ② VERT                    ③ REFACTOR
   ┌──────────────┐            ┌──────────────┐          ┌──────────────┐
   │ J'écris un   │            │ J'écris le   │          │ Je nettoie   │
   │ test qui     │  ──────▶   │ minimum de   │ ──────▶  │ le code, en  │
   │ ÉCHOUE       │            │ code pour le │          │ gardant les  │
   │              │            │ faire passer │          │ tests verts  │
   └──────────────┘            └──────────────┘          └──────────────┘
```

- **Rouge** :
  - j'écris un test qui décrit le comportement attendu… et je vérifie
   qu'il **échoue**. Un test qui passe tout de suite ne prouve rien.
- **Vert** :
  - j'écris juste assez de code pour que le test passe.
- **Refactor** :
  - je nettoie le code sans casser les tests.

> [!Info]
> **Pourquoi écrire le test d'abord ?**
> - Parce qu'un test écrit *après* le code vérifie seulement « ce que le code fait », alors qu'un test écrit *avant* dit « ce que le code **doit** faire ». C'est toute la différence.

Nous utiliserons **pytest**. Un test, c'est une simple fonction :

```python
def test_addition():
    assert 2 + 2 == 4
```

---

## 5. Comment lire un chapitre

Chaque chapitre de code suit le même schéma :

1. **Le problème** : qu'est-ce qu'on cherche à faire ?
2. **La théorie** : les concepts Python/pygame nécessaires.
3. **À vous de jouer !** : l'exercice, avec le **test à écrire d'abord**.
4. **Le corrigé** : le code complet, expliqué.
5. **En résumé** : les points clés.

Prenez le temps de **taper** le code plutôt que de le copier : c'est en écrivant
qu'on apprend. Et lancez les tests à chaque étape.

---

## En résumé

- Le **Pong** est un petit jeu, mais il contient tout ce qui fait un vrai jeu.
- Le projet est découpé en **couches** : logique d'un côté (testable), affichage de
  l'autre, constantes regroupées dans `settings.py`.
- On développe en **TDD** : **rouge → vert → refactor**.

---

## Étape suivante

[**01. L'environnement >>>**](01-environnement.md)
