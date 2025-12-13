#!/usr/bin/env python3
"""
Calcule la réduction moyenne de nœuds (Base vs MO / TT / TT+MO)
pour les phases `opening`, `midgame`, `endgame`, depths 1..4.
Répète chaque configuration `N_TRIALS` fois (moyenne + écart-type).
Résultats sauvegardés dans `node_reduction_by_phase.csv`.
"""

import random
import csv
import statistics
from collections import OrderedDict
from game.board import Board
from ai.heuristics import evaluate

MAX_TT_ENTRIES = 50000
N_TRIALS = 10
PHASES = ['opening', 'midgame', 'endgame']
DEPTHS = [1,2,3,4]

# utility: generate deterministic positions per phase/trial
def create_phase_position(phase, seed):
    random.seed(seed)
    board = Board()
    if phase == 'opening':
        return board, 1
    player = 1
    moves = 0
    target = 12 if phase == 'midgame' else 48
    while moves < target:
        valid = board.get_valid_moves(player)
        if not valid:
            player = -player
            valid = board.get_valid_moves(player)
        if not valid:
            break
        move = random.choice(valid)
        board.make_move(move, player)
        player = -player
        moves += 1
    return board, player

# counting search (nodes)

def count_nodes(board, player, depth, use_tt, use_mo, heuristic='new'):
    global TT
    TT = OrderedDict()
    TT['_nodes'] = 0

    def quick_eval_new(move, b=None, p=None):
        # lightweight inline eval: corners + dangerous + flips
        (r,c) = move
        if isinstance(c, str):
            c = ord(c.strip().upper()) - ord('A') if c.strip().isalpha() else int(c)
        if isinstance(r, str):
            r = int(r.strip()) if r.strip().isdigit() else r
        r_idx = (r-1) if isinstance(r,int) and 1<=r<=8 else (r if isinstance(r,int) else 0)
        r_idx = max(0, min(7, r_idx))
        c = max(0, min(7, c))
        score = 0
        corners = [(0,0),(0,7),(7,0),(7,7)]
        if (r_idx,c) in corners:
            score += 1000
        dangerous = [(0,1),(1,0),(1,1),(0,6),(1,6),(1,7),(6,0),(6,1),(7,1),(6,6),(6,7),(7,6)]
        if (r_idx,c) in dangerous:
            score -= 500
        edges = [(i,j) for i in range(8) for j in range(8) if i in (0,7) or j in (0,7)]
        if (r_idx,c) in edges and (r_idx,c) not in corners and (r_idx,c) not in dangerous:
            score += 50
        if b is not None and p is not None:
            flipped = b.make_move((r,c), p)
            score += len(flipped)*10
            b.undo_move((r,c), flipped, p)
        return score

    def quick_eval_old(move):
        from ai.heuristics_consts import PST
        r,c = move
        if isinstance(c,str):
            c = ord(c.strip().upper()) - ord('A') if c.strip().isalpha() else int(c)
        if isinstance(r,str):
            r = int(r.strip()) if r.strip().isdigit() else r
        r_idx = (r-1) if isinstance(r,int) and 1<=r<=8 else (r if isinstance(r,int) else 0)
        r_idx = max(0, min(7, r_idx))
        c = max(0, min(7, c))
        return PST[r_idx][c]

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
        # Move ordering aligné avec minimax: seulement profondeur >= 4
        if use_mo and d >= 4:
            if heuristic == 'new':
                scored = [(m, quick_eval_new(m, b, p)) for m in valid]
            else:
                scored = [(m, quick_eval_old(m)) for m in valid]
            scored.sort(key=lambda item: item[1], reverse=True)
            valid = [m for m, _ in scored]
        for mv in valid:
            flipped = b.make_move(mv, p)
            child = -search_counting(b, -p, d-1, -beta, -alpha)
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

# run experiments
rows = []
for phase in PHASES:
    for depth in DEPTHS:
        base_list = []
        tt_list = []
        mo_list = []
        both_list = []
        for t in range(N_TRIALS):
            seed = hash((phase, depth, t)) & 0xffffffff
            board, player = create_phase_position(phase, seed)
            # copy board for each run (make_move mutates)
            import copy
            b1 = copy.deepcopy(board)
            b2 = copy.deepcopy(board)
            b3 = copy.deepcopy(board)
            b4 = copy.deepcopy(board)
            base_nodes = count_nodes(b1, player, depth, use_tt=False, use_mo=False)
            tt_nodes = count_nodes(b2, player, depth, use_tt=True, use_mo=False)
            mo_nodes = count_nodes(b3, player, depth, use_tt=False, use_mo=True)
            both_nodes = count_nodes(b4, player, depth, use_tt=True, use_mo=True)
            base_list.append(base_nodes)
            tt_list.append(tt_nodes)
            mo_list.append(mo_nodes)
            both_list.append(both_nodes)
        # stats
        base_mean = statistics.mean(base_list)
        base_std = statistics.pstdev(base_list)
        tt_mean = statistics.mean(tt_list)
        tt_std = statistics.pstdev(tt_list)
        mo_mean = statistics.mean(mo_list)
        mo_std = statistics.pstdev(mo_list)
        both_mean = statistics.mean(both_list)
        both_std = statistics.pstdev(both_list)
        def red(base, var):
            return ((base - var) / base * 100) if base>0 else 0
        rows.append([phase, depth, 'base', int(base_mean), round(base_std,1), 0.0])
        rows.append([phase, depth, 'tt', int(tt_mean), round(tt_std,1), round(red(base_mean, tt_mean),2)])
        rows.append([phase, depth, 'mo', int(mo_mean), round(mo_std,1), round(red(base_mean, mo_mean),2)])
        rows.append([phase, depth, 'tt+mo', int(both_mean), round(both_std,1), round(red(base_mean, both_mean),2)])

# write CSV
csv_path = 'node_reduction_by_phase.csv'
with open(csv_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['phase','depth','variant','mean_nodes','std_nodes','reduction_pct_vs_base'])
    for r in rows:
        w.writerow(r)

# print summary tables
from tabulate import tabulate
for phase in PHASES:
    print(f"\n=== {phase.upper()} ===")
    data = [r for r in rows if r[0]==phase]
    table = []
    for depth in DEPTHS:
        block = [x for x in data if x[1]==depth]
        table.append([f"Depth {depth}", "", "", ""])
        for entry in block:
            _,_,variant,mean,std,redpct = entry
            table.append(["", variant, mean, f"{std}", f"{redpct}%"]) 
    print(tabulate(table, headers=['', 'Variant', 'Mean nodes', 'Std', 'Reduction vs base'], tablefmt='grid'))

print(f"\nResults saved to {csv_path}")
