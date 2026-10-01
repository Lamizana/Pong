# 01 — Installation

## Prérequis

- **Python 3.9 ou plus récent** (`python3 --version`).
- Un **terminal** (sous Windows : PowerShell).
- Pas de bibliothèque graphique à installer manuellement : tout est dans `pip`.

## 1. Récupérer le projet

```bash
git clone <url-du-depot> Pong
cd Pong
```

## 2. Créer un environnement virtuel

Un **environnement virtuel** (`venv`) est un espace isolé où l'on installe les
dépendances du projet, sans polluer le Python du système.

### Avec `uv` (rapide, recommandé si installé)

```bash
uv venv
uv pip install -r requirements-dev.txt
```

### Avec `venv` + `pip` (version classique)

```bash
python3 -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
```

> **Pourquoi `requirements-dev.txt` et pas `requirements.txt` ?**
> `requirements.txt` ne contient que ce qu'il faut pour *jouer* (pygame).
> `requirements-dev.txt` ajoute les outils de *développement* : `pytest` (tests)
> et `pyinstaller` (création des exécutables).

## 3. Lancer le jeu

```bash
python main.py
```

Une fenêtre s'ouvre sur le menu principal. Utilise **↑ / ↓** (ou **Z / S**) pour
naviguer et **Entrée** pour valider.

## 4. Lancer les tests

```bash
pytest
```

Tu dois voir une ligne du type `45 passed`. Ces tests vérifient la physique, l'IA,
le score et le parcours des scènes, **sans ouvrir de fenêtre**.

## 5. (Optionnel) Vérifier le packaging

```bash
./build.sh          # Linux : produit dist/Pong
```

Sous Windows :

```powershell
.\build.ps1         # produit dist\Pong.exe
```

Nous détaillons le packaging au [chapitre 11](11-packaging-deploiement.md).

## En cas de problème

| Symptôme | Piste |
|----------|-------|
| `ModuleNotFoundError: pygame` | Le venv n'est pas activé, ou les dépendances ne sont pas installées. |
| Pas de son | Normal en environnement sans carte audio : le jeu se met en silence. |
| `python` introuvable sous Linux | Utilise `python3`. |

## Étape suivante

→ [02 — Structure du projet](02-structure-du-projet.md)
