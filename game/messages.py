import itertools 
import threading
import time
from rich.console import Console

console = Console()

def ai_loader(stop_event):
    frames = ["⠋ ", "⠙ ", "⠹ ", "⠸ ", "⠼ ", "⠴ ", "⠦ ", "⠧ ", "⠇ ", "⠏ "]
    for frame in itertools.cycle(frames):
        if stop_event.is_set():
            break
        print(f"\rAI thinking {frame}", end="", flush=True)
        time.sleep(0.1)
    print("\r" + " " * 20 + "\r", end="")

MSG_WELCOME = "\n[bold cyan]Welcome to Reversi![/bold cyan]\n__________________________________\n"

MSG_DEPTH_CHOICE = "Select AI depth ([bold bright_green]1 easy[/bold bright_green] - [bold bright_red]5 hard[/bold bright_red]): "
MSG_DEPTH_CHOICE_1 = "Select AI 1 depth ([bold bright_green]1 easy[/bold bright_green] - [bold bright_red]5 hard[/bold bright_red]): "
MSG_DEPTH_CHOICE_2 = "Select AI 2 depth ([bold bright_green]1 easy[/bold bright_green] - [bold bright_red]5 hard[/bold bright_red]): "

MSG_GAMESTARTED = "\n[bold]Game started![/bold]"

MSG_BLUETURN = "Current player : [bold bright_cyan]Blue[/bold bright_cyan]"
MSG_PINKTURN = "Current player : [bold bright_magenta]Pink[/bold bright_magenta]"

MSG_SKIPTURN = "[bold grey53]No valid moves available, skipping turn.[/bold grey53]"

MSG_BLUEWINS = "[bold bright_cyan]Blue wins![/bold bright_cyan]"
MSG_PINKWINS = "[bold bright_magenta]Pink wins![/bold bright_magenta]"
MSG_TIE = "[bold white]It's a tie![/bold white]"

MSG_VALIDMOVES = "Valid moves: "
MSG_ENTERMOVE = "Enter your move (colrow): "

ERR_EXPECTEDFORMAT = "Expected format: e.g. D3"
ERR_ROWRANGE = "Row must be between 1 and 8."
ERR_COLRANGE = "Column must be between A–H."
ERR_INVALIDMOVE = "Invalid move. Try again."

ERROR_START = "[red1]"
ERROR_END = "[/red1]"

COLS = "ABCDEFGH"
ROWS = {str(i) for i in range(1, 9)}

COL_CYAN = "[bold bright_cyan]"
COL_MAGENTA = "[bold bright_magenta]"