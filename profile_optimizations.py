"""
Profil les optimisations (Transposition Table et Move Ordering)
Compare le temps, la mémoire et le nombre de nœuds explorés.
"""

import time
import csv
from datetime import datetime
from pathlib import Path
from game.board import Board, BLUE, PINK
from ai.heuristics import evaluate
from ai.heuristics_consts import PST
from collections import OrderedDict
from rich.console import Console
from rich.table import Table
import psutil
import tracemalloc

console = Console()

# Configuration
MAX_TT_ENTRIES = 50000

class ProfiledSearch:
    """Classe pour profiler différentes variantes du minimax"""
    
    def __init__(self, use_tt=True, use_move_ordering=True):
        self.use_tt = use_tt
        self.use_move_ordering = use_move_ordering
        self.TT = OrderedDict()
        self.node_count = 0
        
    def quick_eval(self, move):
        """Évaluation rapide d'une position pour move ordering"""
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
    
    def search(self, board, player, depth, alpha=float('-inf'), beta=float('inf')):
        """Minimax avec alpha-bêta"""
        self.node_count += 1
        
        # Transposition table lookup
        key = None
        if self.use_tt and depth >= 2:
            key = (tuple(map(tuple, board.grid)), player, depth)
            if key in self.TT:
                return self.TT[key]
        
        best_score = float('-inf')
        
        # Cas terminaux
        if board.is_terminal():
            return board.score(player)
        if depth == 0:
            return evaluate(board, player)
        
        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            return -self.search(board, -player, depth, -beta, -alpha)
        
        # Move ordering
        if self.use_move_ordering:
            valid_moves.sort(key=self.quick_eval, reverse=True)
        
        # Exploration
        for move in valid_moves:
            flipped = board.make_move(move, player)
            child_score = -self.search(board, -player, depth - 1, -beta, -alpha)
            board.undo_move(move, flipped, player)
            
            best_score = max(best_score, child_score)
            alpha = max(alpha, child_score)
            if alpha >= beta:
                break
        
        # Transposition table store
        if self.use_tt and key is not None:
            self.TT[key] = best_score
            if len(self.TT) > MAX_TT_ENTRIES:
                self.TT.popitem(last=False)
        
        return best_score


def profile_variant(board, player, depth, use_tt, use_move_ordering, variant_name):
    """Profil une variante particulière"""
    console.print(f"\n[cyan]Profilage : {variant_name}[/cyan]")
    
    profiler = ProfiledSearch(use_tt=use_tt, use_move_ordering=use_move_ordering)
    
    # Mémoire
    proc = psutil.Process()
    tracemalloc.start()
    rss_before = proc.memory_info().rss
    
    # Temps
    start_time = time.time()
    score = profiler.search(board, player, depth)
    elapsed = time.time() - start_time
    
    # Résultats mémoire
    rss_after = proc.memory_info().rss
    tr_current, tr_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    rss_delta = (rss_after - rss_before) / 1024**2  # MB
    tr_peak_kb = tr_peak / 1024  # KB
    
    result = {
        'variant': variant_name,
        'use_tt': use_tt,
        'use_move_ordering': use_move_ordering,
        'depth': depth,
        'time_sec': round(elapsed, 3),
        'nodes_explored': profiler.node_count,
        'rss_delta_mb': round(rss_delta, 2),
        'tracemalloc_peak_kb': int(tr_peak_kb),
        'tt_size': len(profiler.TT),
        'score': score,
    }
    
    console.print(f"  ⏱️  Temps: {elapsed:.3f}s")
    console.print(f"  📊 Nœuds explorés: {profiler.node_count}")
    console.print(f"  💾 RSS delta: {rss_delta:.2f} MB")
    console.print(f"  🧠 Tracemalloc peak: {tr_peak_kb:.0f} KB")
    console.print(f"  📈 TT size: {len(profiler.TT)}")
    
    return result


def main():
    """Profile différentes variantes"""
    console.print("[bold green]╔════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║    PROFIL DES OPTIMISATIONS             ║[/bold green]")
    console.print("[bold green]╚════════════════════════════════════════╝[/bold green]")
    
    # Créer une position de départ
    board = Board()
    player = BLUE
    
    results = []
    
    # Tester sur plusieurs profondeurs
    for depth in [2, 3, 4]:
        console.print(f"\n[bold cyan]═══ Profondeur {depth} ═══[/bold cyan]")
        
        # Créer une copie du plateau pour chaque test
        test_board = board.clone()
        
        # Variant 1: Pas de TT, pas de move ordering
        result1 = profile_variant(
            test_board.clone(), player, depth,
            use_tt=False, use_move_ordering=False,
            variant_name="Base (pas TT, pas MO)"
        )
        results.append(result1)
        
        # Variant 2: TT seulement
        result2 = profile_variant(
            test_board.clone(), player, depth,
            use_tt=True, use_move_ordering=False,
            variant_name="TT seulement"
        )
        results.append(result2)
        
        # Variant 3: Move ordering seulement
        result3 = profile_variant(
            test_board.clone(), player, depth,
            use_tt=False, use_move_ordering=True,
            variant_name="Move Ordering seulement"
        )
        results.append(result3)
        
        # Variant 4: TT + Move ordering (complet)
        result4 = profile_variant(
            test_board.clone(), player, depth,
            use_tt=True, use_move_ordering=True,
            variant_name="TT + Move Ordering (complet)"
        )
        results.append(result4)
    
    # Sauvegarde CSV
    output_file = Path("profile_optimizations.csv")
    fieldnames = results[0].keys()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    console.print(f"\n[bold green]✓ Résultats sauvegardés : {output_file}[/bold green]")
    
    # Afficher table comparée
    _display_comparison_table(results)


def _display_comparison_table(results):
    """Affiche une table de comparaison par profondeur"""
    console.print("\n[bold cyan]═══ TABLEAU COMPARATIF ═══[/bold cyan]\n")
    
    for depth in [2, 3, 4]:
        depth_results = [r for r in results if r['depth'] == depth]
        
        table = Table(title=f"Profondeur {depth}")
        table.add_column("Variante", style="cyan")
        table.add_column("Temps (s)", style="magenta")
        table.add_column("Nœuds", style="yellow")
        table.add_column("RSS Δ (MB)", style="green")
        table.add_column("Mémoire (KB)", style="blue")
        
        for r in depth_results:
            table.add_row(
                r['variant'],
                str(r['time_sec']),
                str(r['nodes_explored']),
                str(r['rss_delta_mb']),
                str(r['tracemalloc_peak_kb']),
            )
        
        console.print(table)
    
    # Calcul des speedups et améliorations
    console.print("\n[bold cyan]═══ GAINS DES OPTIMISATIONS ═══[/bold cyan]\n")
    
    for depth in [2, 3, 4]:
        depth_results = {r['variant']: r for r in results if r['depth'] == depth}
        
        base = depth_results.get("Base (pas TT, pas MO)")
        if base:
            tt_only = depth_results.get("TT seulement")
            mo_only = depth_results.get("Move Ordering seulement")
            full = depth_results.get("TT + Move Ordering (complet)")
            
            table = Table(title=f"Gains à profondeur {depth}")
            table.add_column("Optimisation", style="cyan")
            table.add_column("Speedup temps", style="magenta")
            table.add_column("Réduction nœuds", style="yellow")
            table.add_column("Économie mémoire", style="green")
            
            if tt_only and tt_only['time_sec'] > 0:
                tt_speedup = base['time_sec'] / tt_only['time_sec']
                tt_nodes = (1 - tt_only['nodes_explored'] / base['nodes_explored']) * 100 if base['nodes_explored'] > 0 else 0
                tt_mem = base['tracemalloc_peak_kb'] - tt_only['tracemalloc_peak_kb']
                table.add_row(
                    "TT",
                    f"{tt_speedup:.2f}x",
                    f"{tt_nodes:.1f}%",
                    f"{tt_mem} KB"
                )
            
            if mo_only and mo_only['time_sec'] > 0:
                mo_speedup = base['time_sec'] / mo_only['time_sec']
                mo_nodes = (1 - mo_only['nodes_explored'] / base['nodes_explored']) * 100 if base['nodes_explored'] > 0 else 0
                mo_mem = base['tracemalloc_peak_kb'] - mo_only['tracemalloc_peak_kb']
                table.add_row(
                    "Move Ordering",
                    f"{mo_speedup:.2f}x",
                    f"{mo_nodes:.1f}%",
                    f"{mo_mem} KB"
                )
            
            if full and full['time_sec'] > 0:
                full_speedup = base['time_sec'] / full['time_sec']
                full_nodes = (1 - full['nodes_explored'] / base['nodes_explored']) * 100 if base['nodes_explored'] > 0 else 0
                full_mem = base['tracemalloc_peak_kb'] - full['tracemalloc_peak_kb']
                table.add_row(
                    "TT + MO (complet)",
                    f"{full_speedup:.2f}x",
                    f"{full_nodes:.1f}%",
                    f"{full_mem} KB"
                )
            
            console.print(table)


if __name__ == "__main__":
    main()
