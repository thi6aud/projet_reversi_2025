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
- Humain vs Humain
- Humain vs IA
- IA vs IA

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