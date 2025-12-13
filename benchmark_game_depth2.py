#!/usr/bin/env python3
"""
Lance 20 parties à depth=4 et mesure la réduction de nœuds
par phase du jeu (opening, midgame, endgame).
"""

import random
from collections import OrderedDict, defaultdict
from game.board import Board
from game.player import Player
from ai.heuristics import evaluate

MAX_TT_ENTRIES = 50000
DEPTH = 4
NUM_GAMES = 5

def count_nodes_at_move(board, player, depth, use_tt, use_mo):
    """Compte les nœuds pour un coup à partir d'une position."""
    global TT
    TT = OrderedDict()
    TT['_nodes'] = 0
    
    def quick_eval_new(move, b=None, p=None):
        (r, c) = move
        if isinstance(c, str):
            c = ord(c.strip().upper()) - ord('A') if c.strip().isalpha() else int(c)
        if isinstance(r, str):
            r = int(r.strip()) if r.strip().isdigit() else r
        r_idx = (r - 1) if isinstance(r, int) and 1 <= r <= 8 else (r if isinstance(r, int) else 0)
        r_idx = max(0, min(7, r_idx))
        c = max(0, min(7, c))
        score = 0
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        if (r_idx, c) in corners:
            score += 1000
        dangerous = [(0, 1), (1, 0), (1, 1), (0, 6), (1, 6), (1, 7), (6, 0), (6, 1), (7, 1), (6, 6), (6, 7), (7, 6)]
        if (r_idx, c) in dangerous:
            score -= 500
        edges = [(i, j) for i in range(8) for j in range(8) if i in (0, 7) or j in (0, 7)]
        if (r_idx, c) in edges and (r_idx, c) not in corners and (r_idx, c) not in dangerous:
            score += 50
        if b is not None and p is not None:
            flipped = b.make_move((r, c), p)
            score += len(flipped) * 10
            b.undo_move((r, c), flipped, p)
        return score

    def search_counting(b, p, d, alpha=float('-inf'), beta=float('inf')):
        TT['_nodes'] += 1
        key = None
        if use_tt and d >= 3:
            key = (tuple(map(tuple, b.grid)), p, d)
            if key in TT:
                return TT[key]
        best_score = float('-inf')
        if b.is_terminal():
            return b.score(p)
        if d == 0:
            return evaluate(b, p)
        valid = b.get_valid_moves(p)
        if not valid:
            return -search_counting(b, -p, d, -beta, -alpha)
        # Move ordering seulement en midgame et depth >= 4
        if use_mo and d >= 4:
            total = sum(1 for row in b.grid for cell in row if cell != 0)
            is_midgame = 13 <= total <= 48
            if is_midgame:
                scored = [(m, quick_eval_new(m, b, p)) for m in valid]
                scored.sort(key=lambda item: item[1], reverse=True)
                valid = [m for m, _ in scored]
        for mv in valid:
            flipped = b.make_move(mv, p)
            child = -search_counting(b, -p, d - 1, -beta, -alpha)
            b.undo_move(mv, flipped, p)
            best_score = max(best_score, child)
            alpha = max(alpha, child)
            if alpha >= beta:
                break
        if use_tt and key is not None:
            TT[key] = best_score
            if len(TT) > MAX_TT_ENTRIES:
                TT.popitem(last=False)
        return best_score

    search_counting(board, player, depth)
    nodes = TT.pop('_nodes', 0)
    return nodes

def get_phase(board):
    """Détermine la phase du jeu."""
    total_pieces = sum(1 for row in board.grid for cell in row if cell != 0)
    if total_pieces <= 12:
        return 'opening'
    elif total_pieces <= 48:
        return 'midgame'
    else:
        return 'endgame'

print(f"╔══════════════════════════════════════════════════╗")
print(f"║  Benchmark: 20 parties à depth={DEPTH}            ║")
print(f"║  Mesure réduction nœuds par phase              ║")
print(f"╚══════════════════════════════════════════════════╝\n")

phase_data = defaultdict(list)  # phase -> list of (base_nodes, mo_nodes)

for game_num in range(NUM_GAMES):
    print(f"Partie {game_num + 1}/{NUM_GAMES}...", end=" ", flush=True)
    board = Board()
    player = 1
    moves_count = 0

    while True:
        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            player = -player
            valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            break

        # Mesurer la réduction de nœuds
        import copy
        b1 = copy.deepcopy(board)
        b2 = copy.deepcopy(board)
        
        base_nodes = count_nodes_at_move(b1, player, DEPTH, use_tt=False, use_mo=False)
        mo_nodes = count_nodes_at_move(b2, player, DEPTH, use_tt=False, use_mo=True)
        
        phase = get_phase(board)
        phase_data[phase].append((base_nodes, mo_nodes))
        
        # Jouer un coup aléatoire
        move = random.choice(valid_moves)
        board.make_move(move, player)
        player = -player
        moves_count += 1

    print(f"✓ ({moves_count} coups)")

# Afficher résultats
from tabulate import tabulate
import statistics

print(f"\n╔══════════════════════════════════════════════════╗")
print(f"║  RÉSULTATS FINAUX                               ║")
print(f"╚══════════════════════════════════════════════════╝\n")

for phase in ['opening', 'midgame', 'endgame']:
    if phase not in phase_data:
        print(f"{phase.upper()}: aucun coup")
        continue
    
    data = phase_data[phase]
    base_nodes_list = [b for b, _ in data]
    mo_nodes_list = [m for _, m in data]
    
    base_mean = statistics.mean(base_nodes_list)
    mo_mean = statistics.mean(mo_nodes_list)
    reduction = ((base_mean - mo_mean) / base_mean * 100) if base_mean > 0 else 0
    
    table_data = [
        ['Base (pas MO)', f"{base_mean:.0f}", f"{statistics.stdev(base_nodes_list) if len(base_nodes_list) > 1 else 0:.1f}"],
        ['MO activé', f"{mo_mean:.0f}", f"{statistics.stdev(mo_nodes_list) if len(mo_nodes_list) > 1 else 0:.1f}"],
        ['', '', ''],
        ['Réduction nœuds', f"{reduction:.2f}%", f"({len(data)} coups)"],
    ]
    print(f"=== {phase.upper()} ===\n")
    print(tabulate(table_data, headers=['Variante', 'Nœuds moyens', 'Std'], tablefmt='grid'))
    print()

# CSV export
import csv
with open('game_benchmark_depth2.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['phase', 'move_index', 'base_nodes', 'mo_nodes', 'reduction_pct'])
    idx = 0
    for phase in ['opening', 'midgame', 'endgame']:
        if phase in phase_data:
            for i, (base, mo) in enumerate(phase_data[phase]):
                reduction_pct = ((base - mo) / base * 100) if base > 0 else 0
                w.writerow([phase, i, base, mo, round(reduction_pct, 2)])

print(f"✓ Résultats sauvegardés : game_benchmark_depth2.csv")
