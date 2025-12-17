
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

