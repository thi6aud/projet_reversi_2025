from typing import Tuple, List, Dict
import time
import tracemalloc
import psutil
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TimeElapsedColumn, SpinnerColumn, TextColumn

import os
import sys

# Ensure project root is on sys.path when running from benchmarks/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from game.board import Board, BLUE, PINK
from game.player import AIPlayer, RandomAIPlayer
import ai.minimax as mm

console = Console()
process = psutil.Process()

# Monkey-patchable node counter
class NodeCounter:
    def __init__(self):
        self.count = 0
    def reset(self):
        self.count = 0
    def inc(self):
        self.count += 1

NODE_COUNTER = NodeCounter()

# Wrap mm.search to count nodes
_original_search = mm.search

def counting_search(board, player, depth, alpha=float('-inf'), beta=float('inf')):
    NODE_COUNTER.inc()
    return _original_search(board, player, depth, alpha, beta)

# Helper to disable move ordering (baseline)
_original_quick_eval = mm.quick_eval

def disable_ordering_quick_eval(*args, **kwargs):
    # Return constant score to avoid reordering
    return 0


def get_phase(board: Board) -> str:
    return mm.get_game_phase(board)


def format_bytes(bytes_val: int) -> str:
    """Format bytes to KB or MB for readability."""
    if bytes_val >= 1_000_000:
        return f"{bytes_val / 1_000_000:.1f} MB"
    else:
        return f"{bytes_val / 1_000:.1f} KB"


def prompt_int(msg: str, valid: Tuple[int, int], default: int | None = None) -> int:
    lo, hi = valid
    while True:
        try:
            raw = input(msg).strip()
        except (EOFError, KeyboardInterrupt):
            if default is not None:
                console.print(f"[yellow]No input detected, using default {default}[/yellow]")
                return default
            raise
        try:
            val = int(raw)
        except Exception:
            if default is not None and raw == "":
                console.print(f"[yellow]Using default {default}[/yellow]")
                return default
            console.print(f"[red]Please enter a number between {lo} and {hi}[/red]")
            continue
        if lo <= val <= hi:
            return val
        console.print(f"[red]Please enter a number between {lo} and {hi}[/red]")


def setup_benchmark():
    console.print("\n[bold cyan]═══════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]     Reversi AI Benchmark Setup[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════[/bold cyan]\n")
    
    console.print("[yellow]Matchup:[/yellow]")
    console.print("  1) AI vs AI")
    console.print("  2) Random vs AI")
    mode = prompt_int("  Choose (1-2): ", (1, 2), default=1)
    
    console.print("\n[yellow]AI Depth:[/yellow]")
    if mode == 1:
        depth1 = prompt_int("  BLUE depth (1-5): ", (1, 5), default=4)
        depth2 = prompt_int("  PINK depth (1-5): ", (1, 5), default=4)
    else:
        depth2 = prompt_int("  AI depth (1-5): ", (1, 5), default=4)
        depth1 = None  # Random AI has no depth
    
    console.print("\n[yellow]Starter:[/yellow]")
    console.print("  1) BLUE starts")
    console.print("  2) PINK starts")
    console.print("  3) Switch each game (fair)")
    starter = prompt_int("  Choose (1-3): ", (1, 3), default=3)
    
    console.print("\n[yellow]Games:[/yellow]")
    games = prompt_int("  Number of games (1-100): ", (1, 100), default=5)
    
    console.print("\n[dim]Running with current optimization variant...[/dim]\n")
    variant = 1  # Always use current version
    return mode, depth1, depth2, starter, games, variant


def make_players(mode: int, depth1: int | None, depth2: int) -> Tuple:
    if mode == 1:
        return AIPlayer(BLUE, depth=depth1), AIPlayer(PINK, depth=depth2)
    else:
        return RandomAIPlayer(BLUE), AIPlayer(PINK, depth=depth2)


def get_player_label(player) -> str:
    """Get a descriptive label for a player."""
    if isinstance(player, AIPlayer):
        return f"AI (d={player.depth})"
    elif isinstance(player, RandomAIPlayer):
        return "Random"
    else:
        return "Human"


def play_one_game(p1, p2, starter: int, variant: int, progress_callback=None) -> Dict:
    # variant: 0 baseline (no MO), 1 current
    # Install monkey patches
    mm.search = counting_search
    if variant == 0:
        mm.quick_eval = disable_ordering_quick_eval
    else:
        mm.quick_eval = _original_quick_eval

    board = Board()
    current = p1 if starter == 1 else p2
    other = p2 if current is p1 else p1

    # stats per phase, per player
    phase_stats = {
        'opening': {
            'moves': 0, 'time_ms': 0.0, 'rss': [], 'trace_cur': [], 'trace_peak': [], 'nodes': 0,
            'p1_moves': 0, 'p1_time_ms': 0.0, 'p2_moves': 0, 'p2_time_ms': 0.0
        },
        'midgame': {
            'moves': 0, 'time_ms': 0.0, 'rss': [], 'trace_cur': [], 'trace_peak': [], 'nodes': 0,
            'p1_moves': 0, 'p1_time_ms': 0.0, 'p2_moves': 0, 'p2_time_ms': 0.0
        },
        'endgame': {
            'moves': 0, 'time_ms': 0.0, 'rss': [], 'trace_cur': [], 'trace_peak': [], 'nodes': 0,
            'p1_moves': 0, 'p1_time_ms': 0.0, 'p2_moves': 0, 'p2_time_ms': 0.0
        },
    }

    tracemalloc.start()
    last_phase = None
    while True:
        valid_current = board.get_valid_moves(current.color)
        valid_other = board.get_valid_moves(other.color)
        if not valid_current and not valid_other:
            break
        if not valid_current:
            current, other = other, current
            continue
        phase = get_phase(board)
        # Detect phase transition and callback
        if last_phase is not None and last_phase != phase and progress_callback:
            progress_callback()
        last_phase = phase
        
        NODE_COUNTER.reset()
        t0 = time.time()
        move = current.get_move(board)
        elapsed_ms = (time.time() - t0) * 1000.0
        if move is None:
            current, other = other, current
            continue
        board.apply_move(move[0], move[1], current.color)
        current, other = other, current
        # memory snapshots
        rss = process.memory_info().rss
        cur, peak = tracemalloc.get_traced_memory()
        ps = phase_stats[phase]
        ps['moves'] += 1
        ps['time_ms'] += elapsed_ms
        ps['rss'].append(rss)
        ps['trace_cur'].append(cur)
        ps['trace_peak'].append(peak)
        ps['nodes'] += NODE_COUNTER.count
        # Per-player timing
        if current == p1:
            ps['p2_moves'] += 1
            ps['p2_time_ms'] += elapsed_ms
        else:
            ps['p1_moves'] += 1
            ps['p1_time_ms'] += elapsed_ms
    # callback for final phase completion
    if progress_callback:
        progress_callback()
    tracemalloc.stop()

    # result
    b, w = board.count_discs()
    winner = 'BLUE' if b > w else ('PINK' if w > b else 'TIE')
    return {
        'phase_stats': phase_stats,
        'winner': winner,
        'p1': p1,
        'p2': p2,
    }


def aggregate(results: List[Dict], mode: int, starter_mode: int, variant: int, games: int, depth1: int | None, depth2: int):
    # who vs who
    who = 'AI vs AI' if mode == 1 else 'Random vs AI'
    starter_label = {1: 'BLUE', 2: 'PINK', 3: 'Switch'}[starter_mode]
    # Build depth string
    if mode == 1:
        depth_str = f"d={depth1} vs d={depth2}"
    else:
        depth_str = f"d={depth2}"
    
    # Get player labels from first result
    p1_label = get_player_label(results[0]['p1']) if results else "P1"
    p2_label = get_player_label(results[0]['p2']) if results else "P2"
    
    # Count wins
    wins = {'BLUE': 0, 'PINK': 0, 'TIE': 0}
    for r in results:
        if r['winner'] in wins:
            wins[r['winner']] += 1
    win_rate_p1 = (wins['BLUE'] / games) * 100.0 if games else 0  # P1 is BLUE
    win_rate_p2 = (wins['PINK'] / games) * 100.0 if games else 0  # P2 is PINK
    win_rate_draw = (wins['TIE'] / games) * 100.0 if games else 0

    # aggregate per phase
    agg = {}
    for phase in ('opening', 'midgame', 'endgame'):
        moves = sum(r['phase_stats'][phase]['moves'] for r in results)
        time_ms = sum(r['phase_stats'][phase]['time_ms'] for r in results)
        rss_all = [x for r in results for x in r['phase_stats'][phase]['rss']]
        cur_all = [x for r in results for x in r['phase_stats'][phase]['trace_cur']]
        peak_all = [x for r in results for x in r['phase_stats'][phase]['trace_peak']]
        nodes = sum(r['phase_stats'][phase]['nodes'] for r in results)
        
        # Per-player stats
        p1_moves = sum(r['phase_stats'][phase]['p1_moves'] for r in results)
        p1_time_ms = sum(r['phase_stats'][phase]['p1_time_ms'] for r in results)
        p2_moves = sum(r['phase_stats'][phase]['p2_moves'] for r in results)
        p2_time_ms = sum(r['phase_stats'][phase]['p2_time_ms'] for r in results)
        
        avg_time_per_move = (time_ms / moves) if moves else 0.0
        p1_avg_time = (p1_time_ms / p1_moves) if p1_moves else 0.0
        p2_avg_time = (p2_time_ms / p2_moves) if p2_moves else 0.0
        
        mean_rss = (sum(rss_all) / len(rss_all)) if rss_all else 0.0
        mean_trace_cur = (sum(cur_all) / len(cur_all)) if cur_all else 0.0
        mean_trace_peak = (sum(peak_all) / len(peak_all)) if peak_all else 0.0
        agg[phase] = {
            'moves': moves,
            'avg_time_ms': avg_time_per_move,
            'p1_avg_time_ms': p1_avg_time,
            'p2_avg_time_ms': p2_avg_time,
            'mean_rss': mean_rss,
            'mean_trace_cur': mean_trace_cur,
            'mean_trace_peak': mean_trace_peak,
            'nodes': nodes,
        }

    # tables
    tables = {}
    for phase in ('opening', 'midgame', 'endgame'):
        t = Table(title=f"{phase.title()} Phase Results")
        t.add_column("Matchup", justify="left")
        t.add_column("Starter", justify="center")
        t.add_column(f"{p1_label} ms/move", justify="right")
        t.add_column(f"{p2_label} ms/move", justify="right")
        t.add_column(f"{p1_label} % Win", justify="right")
        t.add_column(f"{p2_label} % Win", justify="right")
        t.add_column("Draw %", justify="right")
        t.add_column("Mean RSS", justify="right")
        t.add_column("Mean tracemalloc cur", justify="right")
        t.add_column("Mean tracemalloc peak", justify="right")
        data = agg[phase]
        if phase == 'endgame':
            win_p1 = f"{win_rate_p1:.1f}"
            win_p2 = f"{win_rate_p2:.1f}"
            win_draw = f"{win_rate_draw:.1f}"
        else:
            win_p1 = "-"
            win_p2 = "-"
            win_draw = "-"
        t.add_row(
            f"{who} ({depth_str})",
            starter_label,
            f"{data['p1_avg_time_ms']:.2f}",
            f"{data['p2_avg_time_ms']:.2f}",
            win_p1,
            win_p2,
            win_draw,
            format_bytes(int(data['mean_rss'])),
            format_bytes(int(data['mean_trace_cur'])),
            format_bytes(int(data['mean_trace_peak'])),
        )
        tables[phase] = t
    return tables


def main():
    mode, depth1, depth2, starter_mode, games, variant = setup_benchmark()
    # switching logic with phase-level progress
    results = []
    # Total phases: 3 per game (opening, midgame, endgame)
    total_phases = games * 3
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold]Running benchmarks[/bold]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("bench", total=total_phases)
        for i in range(games):
            if starter_mode == 3:
                starter = 1 if (i % 2 == 0) else 2
            else:
                starter = starter_mode
            p1, p2 = make_players(mode, depth1, depth2)
            # Pass a callback that advances progress bar per phase
            def phase_done():
                progress.advance(task, 1)
            res = play_one_game(p1, p2, starter, variant, progress_callback=phase_done)
            results.append(res)
    tables = aggregate(results, mode, starter_mode, variant, games, depth1, depth2)
    for phase in ('opening', 'midgame', 'endgame'):
        console.print(tables[phase])

if __name__ == "__main__":
    main()
