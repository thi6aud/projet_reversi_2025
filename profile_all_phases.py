#!/usr/bin/env python3
"""
Profil des optimisations (TT + Move Ordering) sur les 3 phases du jeu.
"""

import time
import psutil
import tracemalloc
import csv
from collections import OrderedDict
from game.board import Board
from game.player import Player
from ai.heuristics import evaluate

# Transposition table setup
MAX_TT_ENTRIES = 50000

def create_phase_position(phase):
    """Crée une position typique pour chaque phase."""
    board = Board()
    
    if phase == "opening":
        # Position initiale ou quasi-initiale (ouverture)
        return board, 1  # 1 = bleu
    
    elif phase == "midgame":
        # Générer une position de milieu de partie
        # On joue quelques coups aléatoires
        player = 1
        for _ in range(12):  # ~12 coups
            valid_moves = board.get_valid_moves(player)
            if not valid_moves:
                player = -player
                valid_moves = board.get_valid_moves(player)
            if not valid_moves:
                break
            import random
            move = random.choice(valid_moves)
            board.make_move(move, player)
            player = -player
        return board, player
    
    elif phase == "endgame":
        # Générer une position de fin de partie (presque tous les coups joués)
        player = 1
        for _ in range(48):  # Jouer jusqu'au bout ou presque
            valid_moves = board.get_valid_moves(player)
            if not valid_moves:
                player = -player
                valid_moves = board.get_valid_moves(player)
            if not valid_moves:
                break
            import random
            move = random.choice(valid_moves)
            board.make_move(move, player)
            player = -player
        return board, player

def quick_eval_old(move):
    """Ancienne heuristique (PST statique)."""
    from ai.heuristics_consts import PST
    row, col = move
    
    if isinstance(col, str):
        col_str = col.strip().upper()
        if len(col_str) == 1 and col_str.isalpha():
            col = ord(col_str) - ord('A')
        elif col_str.isdigit():
            col = int(col_str)
    if not isinstance(col, int):
        col = 0

    if isinstance(row, str):
        row_str = row.strip()
        if row_str.isdigit():
            row = int(row_str)

    if isinstance(row, int) and 1 <= row <= 8:
        row_idx = row - 1
    elif isinstance(row, int):
        row_idx = row
    else:
        row_idx = 0

    row_idx = max(0, min(7, row_idx))
    col = max(0, min(7, col))

    return PST[row_idx][col]

def quick_eval_new(move, board=None, player=None):
    """Nouvelle heuristique améliorée."""
    row, col = move
    
    if isinstance(col, str):
        col_str = col.strip().upper()
        if len(col_str) == 1 and col_str.isalpha():
            col = ord(col_str) - ord('A')
        elif col_str.isdigit():
            col = int(col_str)
    if not isinstance(col, int):
        col = 0

    if isinstance(row, str):
        row_str = row.strip()
        if row_str.isdigit():
            row = int(row_str)

    if isinstance(row, int) and 1 <= row <= 8:
        row_idx = row - 1
    elif isinstance(row, int):
        row_idx = row
    else:
        row_idx = 0

    row_idx = max(0, min(7, row_idx))
    col = max(0, min(7, col))

    score = 0

    # Coins
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    if (row_idx, col) in corners:
        score += 1000

    # Carrés dangereux
    dangerous = [
        (0, 1), (1, 0), (1, 1),
        (0, 6), (1, 6), (1, 7),
        (6, 0), (6, 1), (7, 1),
        (6, 6), (6, 7), (7, 6),
    ]
    if (row_idx, col) in dangerous:
        score -= 500

    # Bords (X-squares)
    edges = [(i, j) for i in range(8) for j in range(8) 
             if i in (0, 7) or j in (0, 7)]
    if (row_idx, col) in edges and (row_idx, col) not in corners and (row_idx, col) not in dangerous:
        score += 50

    # Nombre de disques retournés
    if board is not None and player is not None:
        flipped = board.make_move((row, col), player)
        score += len(flipped) * 10
        board.undo_move((row, col), flipped, player)

    return score

def search(board, player, depth, alpha=float('-inf'), beta=float('inf'), 
           use_tt=True, use_mo=True, heuristic='new'):
    """Search avec options pour TT et Move Ordering."""
    global TT
    
    key = None
    if use_tt and depth >= 2:
        key = (tuple(map(tuple, board.grid)), player, depth)
        if key in TT:
            return TT[key]
    
    best_score = float('-inf')
    
    if board.is_terminal():
        return board.score(player)
    
    if depth == 0:
        return evaluate(board, player)
    
    valid_moves = board.get_valid_moves(player)
    
    if not valid_moves:
        return -search(board, -player, depth, -beta, -alpha, use_tt, use_mo, heuristic)
    
    # Move ordering
    if use_mo:
        if heuristic == 'new':
            valid_moves.sort(key=lambda m: quick_eval_new(m, board, player), reverse=True)
        else:
            valid_moves.sort(key=quick_eval_old, reverse=True)
    
    for move in valid_moves:
        flipped = board.make_move(move, player)
        child_score = -search(board, -player, depth-1, -beta, -alpha, use_tt, use_mo, heuristic)
        board.undo_move(move, flipped, player)

        best_score = max(best_score, child_score)
        alpha = max(alpha, child_score)
        if alpha >= beta:
            break
    
    if use_tt and key is not None:
        TT[key] = best_score
        if len(TT) > MAX_TT_ENTRIES:
            TT.popitem(last=False)
    
    return best_score

def benchmark_variant(board, player, depth, use_tt, use_mo, label, heuristic='new'):
    """Benchmark une variante."""
    global TT
    TT = OrderedDict()
    
    # Memory before
    tracemalloc.start()
    mem_before = psutil.Process().memory_info().rss
    
    # Search
    start_time = time.time()
    search(board, player, depth, use_tt=use_tt, use_mo=use_mo, heuristic=heuristic)
    elapsed = time.time() - start_time
    
    mem_after = psutil.Process().memory_info().rss
    memory_delta_kb = (mem_after - mem_before) / 1024
    
    current, peak = tracemalloc.get_traced_memory()
    tt_memory_kb = len(TT) * 200 / 1024  # Rough estimate
    tracemalloc.stop()
    
    return {
        'label': label,
        'time': elapsed,
        'nodes': TT.get('_nodes', 0),  # Will count manually
        'memory_delta_kb': memory_delta_kb,
        'tt_size_kb': tt_memory_kb,
        'tt_entries': len(TT)
    }

def count_nodes(board, player, depth, use_tt, use_mo, heuristic='new'):
    """Compte le nombre de nœuds explorés."""
    global TT
    TT = OrderedDict()
    TT['_nodes'] = 0
    
    def search_counting(b, p, d, alpha=float('-inf'), beta=float('inf')):
        TT['_nodes'] += 1
        
        key = None
        if use_tt and d >= 2:
            key = (tuple(map(tuple, b.grid)), p, d)
            if key in TT:
                return TT[key]
        
        best_score = float('-inf')
        
        if b.is_terminal():
            return b.score(p)
        
        if d == 0:
            return evaluate(b, p)
        
        valid_moves = b.get_valid_moves(p)
        
        if not valid_moves:
            return -search_counting(b, -p, d, -beta, -alpha)
        
        if use_mo:
            if heuristic == 'new':
                valid_moves.sort(key=lambda m: quick_eval_new(m, b, p), reverse=True)
            else:
                valid_moves.sort(key=quick_eval_old, reverse=True)
        
        for move in valid_moves:
            flipped = b.make_move(move, p)
            child_score = -search_counting(b, -p, d-1, -beta, -alpha)
            b.undo_move(move, flipped, p)

            best_score = max(best_score, child_score)
            alpha = max(alpha, child_score)
            if alpha >= beta:
                break
        
        if use_tt and key is not None:
            TT[key] = best_score
            if len(TT) > MAX_TT_ENTRIES:
                TT.popitem(last=False)
        
        return best_score
    
    start_time = time.time()
    search_counting(board, player, depth)
    elapsed = time.time() - start_time
    
    nodes = TT.pop('_nodes', 0)
    
    return {
        'time': elapsed,
        'nodes': nodes,
        'tt_entries': len(TT)
    }

print("╔════════════════════════════════════════╗")
print("║   PROFIL DES OPTIMISATIONS (3 PHASES)  ║")
print("╚════════════════════════════════════════╝")

phases = {
    'opening': [2, 3, 4],
    'midgame': [3, 4, 5],
    'endgame': [3, 4, 5]
}

results_by_phase = {}

for phase_name, depths in phases.items():
    print(f"\n🎮 Phase: {phase_name.upper()}")
    
    # Générer une position
    board, player = create_phase_position(phase_name)
    blue_count = sum(1 for row in board.grid for cell in row if cell == 1)
    red_count = sum(1 for row in board.grid for cell in row if cell == -1)
    print(f"   Position: {blue_count} bleus, {red_count} rouges")
    
    phase_results = []
    
    for depth in depths:
        print(f"\n   Profondeur {depth}:")
        
        # Créer une copie pour chaque test (board est modifié)
        board_copy = Board()
        board_copy.grid = [row[:] for row in board.grid]
        
        # Base (pas TT, pas MO)
        print(f"     Base...", end=" ", flush=True)
        result = count_nodes(board_copy, player, depth, use_tt=False, use_mo=False)
        base_time, base_nodes = result['time'], result['nodes']
        print(f"✓ ({base_time:.3f}s, {base_nodes} nœuds)")
        
        # TT seulement
        print(f"     TT...", end=" ", flush=True)
        result = count_nodes(board_copy, player, depth, use_tt=True, use_mo=False)
        tt_time, tt_nodes = result['time'], result['nodes']
        print(f"✓ ({tt_time:.3f}s, {tt_nodes} nœuds)")
        
        # MO seulement
        print(f"     MO...", end=" ", flush=True)
        result = count_nodes(board_copy, player, depth, use_tt=False, use_mo=True, heuristic='new')
        mo_time, mo_nodes = result['time'], result['nodes']
        print(f"✓ ({mo_time:.3f}s, {mo_nodes} nœuds)")
        
        # TT + MO
        print(f"     TT+MO...", end=" ", flush=True)
        result = count_nodes(board_copy, player, depth, use_tt=True, use_mo=True, heuristic='new')
        both_time, both_nodes = result['time'], result['nodes']
        print(f"✓ ({both_time:.3f}s, {both_nodes} nœuds)")
        
        phase_results.append({
            'depth': depth,
            'base_time': base_time,
            'base_nodes': base_nodes,
            'tt_time': tt_time,
            'tt_nodes': tt_nodes,
            'mo_time': mo_time,
            'mo_nodes': mo_nodes,
            'both_time': both_time,
            'both_nodes': both_nodes,
        })
    
    results_by_phase[phase_name] = phase_results

# Sauvegarder en CSV
csv_file = 'profile_all_phases.csv'
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Phase', 'Depth', 'Base_Time', 'Base_Nodes', 'TT_Time', 'TT_Nodes', 
                     'MO_Time', 'MO_Nodes', 'Both_Time', 'Both_Nodes'])
    for phase, results in results_by_phase.items():
        for r in results:
            writer.writerow([
                phase, r['depth'],
                f"{r['base_time']:.4f}", r['base_nodes'],
                f"{r['tt_time']:.4f}", r['tt_nodes'],
                f"{r['mo_time']:.4f}", r['mo_nodes'],
                f"{r['both_time']:.4f}", r['both_nodes'],
            ])

print(f"\n✓ Résultats sauvegardés : {csv_file}\n")

# Afficher les tableaux
from tabulate import tabulate

for phase_name in ['opening', 'midgame', 'endgame']:
    print(f"\n═══ TABLEAU COMPARATIF - {phase_name.upper()} ═══\n")
    
    results = results_by_phase[phase_name]
    
    for r in results:
        depth = r['depth']
        table_data = [
            ['Base (pas TT, pas MO)', f"{r['base_time']:.3f}", r['base_nodes']],
            ['TT seulement', f"{r['tt_time']:.3f}", r['tt_nodes']],
            ['Move Ordering seulement', f"{r['mo_time']:.3f}", r['mo_nodes']],
            ['TT + Move Ordering', f"{r['both_time']:.3f}", r['both_nodes']],
        ]
        
        print(f"Profondeur {depth}")
        print(tabulate(table_data, headers=['Variante', 'Temps (s)', 'Nœuds'], tablefmt='grid'))
        
        # Gains
        print(f"\nGains:")
        tt_speedup = r['base_time'] / r['tt_time'] if r['tt_time'] > 0 else 0
        mo_speedup = r['base_time'] / r['mo_time'] if r['mo_time'] > 0 else 0
        both_speedup = r['base_time'] / r['both_time'] if r['both_time'] > 0 else 0
        
        mo_reduction = (1 - r['mo_nodes'] / r['base_nodes']) * 100 if r['base_nodes'] > 0 else 0
        both_reduction = (1 - r['both_nodes'] / r['base_nodes']) * 100 if r['base_nodes'] > 0 else 0
        
        gains_data = [
            ['TT', f"{tt_speedup:.2f}x", f"{(1 - r['tt_nodes']/r['base_nodes'])*100:.1f}%"],
            ['MO', f"{mo_speedup:.2f}x", f"{mo_reduction:.1f}%"],
            ['TT+MO', f"{both_speedup:.2f}x", f"{both_reduction:.1f}%"],
        ]
        print(tabulate(gains_data, headers=['Optimisation', 'Speedup', 'Réduction nœuds'], tablefmt='grid'))
        print()
