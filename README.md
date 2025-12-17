≥# Reversi / Othello — projet

Petit projet Reversi (Othello) en Python — console + UI minimale. Le but est d'avoir un jeu jouable en terminal, une IA (minimax) et des utilitaires pour jouer / tester.

## 🧭 Structure du dépôt

- `main.py` — lanceur du jeu
- `game/` — logique du jeu (plateau, gestion, joueurs)
- `ai/` — algorithme IA, heuristiques
- `ui/` — interfaces utilisateur (console, pygame)
- `tests/` — tests unitaires (pytest)

## ⚙️ Prérequis

Ce projet utilise la bibliothèque `rich` pour un rendu terminal amélioré.

Installer les dépendances (recommandé dans un environnement virtuel) :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Si tu veux utiliser l'UI pygame, installe `pygame` et active la UI correspondante (optionnel, mentionné en commentaire dans `requirements.txt`).

## ▶️ Lancer le jeu

```bash
python main.py
```

Le jeu te demandera le mode (humain vs humain, humain vs IA, IA vs IA, profondeur de l'IA, ...). Les coups au terminal s'expriment au format `D3` (colonne lettre A–H + ligne 1–8).

## 🧠 IA

L'IA utilise minimax/alpha-beta (dans `ai/`) et quelques heuristiques simples. Il existe aussi un `RandomAI` pour tester rapidement.

## 🧪 Tests

La suite de tests est prévue dans `tests/` et utilise `pytest` (non obligatoire pour exécution). Pour lancer les tests :

```bash
pip install pytest  # si nécessaire
pytest
```

## 📊 Benchmark — Batteries de tests

Pour collecter des données d'efficacité et comparer différentes configurations d'IA, utilisez le script `benchmark.py` :

### Mode interactif (recommandé pour démarrer)

```bash
python benchmark.py
```

Le script vous posera des questions :
- Nombre de parties à jouer
- Type de joueur 1 (IA Minimax ou RandomAI)
- Profondeur de l'IA (si IA Minimax)
- Type de joueur 2 (IA Minimax ou RandomAI)
- Profondeur (si IA Minimax)
- Nom du fichier CSV de sortie

### Mode programmatique (pour scripts automatisés)

Créez un fichier Python avec votre propre script :

```python
from benchmark import Benchmark

benchmark = Benchmark(output_file="mes_resultats.csv")

# Lancer plusieurs configurations
configs = [
    ({'type': 'AI', 'depth': 4}, {'type': 'AI', 'depth': 3}, "IA Depth 4 vs 3"),
    ({'type': 'AI', 'depth': 5}, {'type': 'RandomAI'}, "IA Depth 5 vs Random"),
]
benchmark.run_multi_batch(10, configs)  # 10 parties par config
benchmark.save_results()
```

### Format du CSV

Le fichier CSV contient les colonnes suivantes :
- `timestamp` — quand la partie a été jouée
- `blue_starts` — qui a commencé (True = BLUE/Player1, False = PINK/Player2)
- `player1_type`, `player1_depth` — type et profondeur du joueur 1 (BLUE)
- `player2_type`, `player2_depth` — type et profondeur du joueur 2 (PINK)
- `winner` — gagnant (`BLUE`, `PINK`, ou `TIE`)
- `blue_score`, `pink_score` — scores finals
- `player1_total_time`, `player1_moves`, `player1_avg_time_ms` — stats temps joueur 1
- `player2_total_time`, `player2_moves`, `player2_avg_time_ms` — stats temps joueur 2

### Caractéristiques du benchmark

- **Alternance des couleurs** : chaque joueur commence alternativement (partie 1 = BLUE, partie 2 = PINK, etc.) pour évaluer équitablement les deux côtés
- **Aléatoire dans l'IA** : quand plusieurs coups ont la même valeur d'évaluation, l'IA en choisit un aléatoirement pour créer de la variabilité entre les parties
- **Table de transposition vidée** : entre chaque partie pour éviter les biais dus à la cache

Ces optimisations garantissent que les tests sont **fiables et non-déterministes**, permettant d'évaluer correctement les performances d'une IA.

Les résultats sont facilement exploitables pour des analyses statistiques dans Excel ou Python.

## Contribuer

Si tu veux améliorer le projet :
- Ajouter des tests pour couvrir le comportement
- Améliorer l'IA (heuristiques / pruning / transposition table)
- Ajouter une interface graphique complète (pygame)

Merci — dis-moi si tu veux :
- un README en anglais
- séparer requirements-dev (tests, lint) et requirements-runtime
- ajouter des exemples ou screenshots
# Reversi 2025

Ce projet est une implémentation du jeu Reversi en Python, avec une interface console et une IA basée sur Minimax.

## Installation

1. Clonez le dépôt :
   ```sh
   git clone https://github.com/thi6aud/projet_reversi_2025.git
   cd projet_reversi_2025
   ```
2. Installez les dépendances :
   ```sh
   pip install -r requirements.txt
   ```

## Utilisation

Lancez le jeu avec :
```sh
python main.py
```
Suivez les instructions dans le terminal pour choisir le mode de jeu :
- Human vs Human
- Human vs AI
- IA random vs Human
- IA random vs AI
- AI vs AI

## Structure du projet

- `main.py` : point d’entrée du jeu
- `game/` : logique du jeu (plateau, joueurs, gestion)
- `ai/` : intelligence artificielle (minimax, heuristiques)
- `ui/` : interfaces utilisateur (console, pygame)
- `tests/` : tests unitaires

## Auteurs

Arsil Ibrahim Saleh, Mahdjoub Amélia, Delucinge Thibaud

## Licence

MIASHS
