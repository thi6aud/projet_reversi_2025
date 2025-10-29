import itertools 
import os
import threading
import time
import sys
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

def print_slowly(text):
    for line in text.splitlines():        # ligne par ligne
        for char in line:                 # caractère par caractère
            console.print(f"[bold cyan]{char}[/bold cyan]", end="")
            time.sleep(0.005)             # petit délai entre chaque char
        print()  # saute une ligne à la fin de chaque ligne

MSG_WELCOME1 = '''
 .S_sSSs      sSSs   .S    S.     sSSs   .S_sSSs      sSSs   .S 
.SS~YS%%b    d%%SP  .SS    SS.   d%%SP  .SS~YS%%b    d%%SP  .SS 
S%S   `S%b  d%S'    S%S    S%S  d%S'    S%S   `S%b  d%S'    S%S 
S%S    S%S  S%S     S%S    S%S  S%S     S%S    S%S  S%|     S%S 
S%S    d*S  S&S     S&S    S%S  S&S     S%S    d*S  S&S     S&S 
S&S   .S*S  S&S_Ss  S&S    S&S  S&S_Ss  S&S   .S*S  Y&Ss    S&S 
S&S_sdSSS   S&S~SP  S&S    S&S  S&S~SP  S&S_sdSSS   `S&&S   S&S 
S&S~YSY%b   S&S     S&S    S&S  S&S     S&S~YSY%b     `S*S  S&S 
S*S   `S%b  S*b     S*b    S*S  S*b     S*S   `S%b     l*S  S*S 
S*S    S%S  S*S.    S*S.   S*S  S*S.    S*S    S%S    .S*P  S*S 
S*S    S&S   SSSbs   SSSbs_S*S   SSSbs  S*S    S&S  sSS*S   S*S 
S*S    SSS    YSSP    YSSP~SSS    YSSP  S*S    SSS  YSS'    S*S 
SP                                      SP                  SP  
Y                                       Y                   Y   
'''

MSG_WELCOME2 = '''
 888888ba                                                     oo 
 88    `8b                                                  
a88aaaa8P'  .d8888b.  dP   .dP  .d8888b.  88d888b.  .d8888b.  dP 
 88   `8b.  88ooood8  88   d8'  88ooood8  88'  `88  Y8ooooo.  88 
 88     88  88.  ...  88 .88'   88.  ...  88              88  88 
 dP     dP  `88888P'  8888P'    `88888P'  dP        `88888P'  dP                                               
'''

MSG_WELCOME3 = '''
MMMMMMMMMMMMM
MM"""""""`MMM                                                    oo 
MM  mmmm,  MM                                                    
M'        .MM  .d8888b.  dP   .dP  .d8888b.  88d888b.  .d8888b.  dP 
MM  MMMb. "MM  88ooood8  88   d8'  88ooood8  88'  `88  Y8ooooo.  88 
MM  MMMMM  MM  88.  ...  88 .88'   88.  ...  88              88  88 
MM  MMMMM  MM  `88888P'  8888P'    `88888P'  dP        `88888P'  dP 
MMMMMMMMMMMMM                                                 
'''

MSG_WELCOME4 = '''
  88bd88b  d8888b  ?88   d8P  d8888b   88bd88b  .d888b,   88b
  88P'  ` d8b_,dPd  88  d8P' d8b_,dP   88P'  `  ?8b,      88P
 d88      88b       8b ,88'  88b      d88         `?8b   d88 
d88'      `?888P'`  ?888P'   `?888P' d88'      `?888P'  d88'    
'''

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
