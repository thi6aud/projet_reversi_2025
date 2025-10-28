import itertools # imports 
import threading
import time
from game.board import Board, BLUE, PINK
from game.player import HumanPlayer, AIPlayer
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

class GameManager:
  def __init__(self):
    self.board = Board()
    self.player1 = None
    self.player2 = None
    self.current_player = None

  def run(self):
    console.print("\n[bold]Welcome to Reversi![/bold]")
    console.print("__________________________________\n")
    mode = console.input("Select mode:\n1. Human vs Human\n2. Human vs AI\n3. AI vs AI\nEnter choice (1-3): ")
    try:
        mode = int(mode)
    except ValueError:
        mode = 1
    if mode == 1:
        self.player1 = HumanPlayer(BLUE)
        self.player2 = HumanPlayer(PINK)
    elif mode == 2:
        self.player1 = HumanPlayer(BLUE)
        depth_choice = console.input("Select AI depth ([bold bright_green]1 easy[/bold bright_green] - [bold bright_red]5 hard[/bold bright_red]): ")
        try:
            depth_choice = int(depth_choice)
        except ValueError:
          depth_choice = 4  # valeur par défaut si l’utilisateur tape n’importe quoi
        depth_choice = max(1, min(depth_choice, 5))  # borne entre 1 et 5
        self.player2 = AIPlayer(PINK, depth=depth_choice)
    else:
        depth_choice1 = console.input("Select AI 1 depth ([bold bright_green]1 easy[/bold bright_green] - [bold bright_red]5 hard[/bold bright_red]): ")
        depth_choice2 = console.input("Select AI 2 depth ([bold bright_green]1 easy[/bold bright_green] - [bold bright_red]5 hard[/bold bright_red]): ")
        try:
            depth_choice1 = int(depth_choice1)
        except ValueError:
            depth_choice1 = 4
        try:
            depth_choice2 = int(depth_choice2)
        except ValueError:
            depth_choice2 = 4
        depth_choice1 = max(1, min(depth_choice1, 5))
        depth_choice2 = max(1, min(depth_choice2, 5))
        self.player1 = AIPlayer(BLUE, depth=depth_choice1)
        self.player2 = AIPlayer(PINK, depth=depth_choice2)
    self.current_player = self.player1
    console.print("\n[bold]Game started![/bold]")
    while True:
      if not self.board.get_valid_moves(self.player1.color) and not self.board.get_valid_moves(self.player2.color):
        break
      self.board.display()
      console.print("Current player :", "[bold bright_cyan]Blue[/bold bright_cyan]" if self.current_player.color == BLUE else "[bold bright_magenta]Pink[/bold bright_magenta]")
      if isinstance(self.current_player, AIPlayer):
          stop_event = threading.Event()
          loader_thread = threading.Thread(target=ai_loader, args=(stop_event,))
          loader_thread.start()
          move = self.current_player.get_move(self.board)
          stop_event.set()
          loader_thread.join()
      else:
          move = self.current_player.get_move(self.board)
      if move is None:
        console.print("[bold grey53]No valid moves available, skipping turn.[/bold grey53]")
      else:
        self.board.apply_move(move[0], move[1], self.current_player.color)
      self.current_player = self.player1 if self.current_player == self.player2 else self.player2
    self.board.display()
    black_count, white_count = self.board.count_discs()
    console.print("[bold bright_cyan]Blue wins![/bold bright_cyan]" if black_count > white_count 
          else "[bold bright_magenta]Pink wins![/bold bright_magenta]" if white_count > black_count 
          else "[bold slate_blue1]It's a tie![/bold slate_blue1]")