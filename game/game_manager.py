import itertools
import threading
import time
from game.board import Board, BLACK, WHITE
from game.player import HumanPlayer, AIPlayer

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
    self.player1 = HumanPlayer(BLACK)
    self.player2 = None
    self.current_player = self.player1

  def run(self):
    depth_choice = input("Select AI depth (1 easy - 4 hard): ")
    try:
        depth_choice = int(depth_choice)
    except ValueError:
      depth_choice = 4  # valeur par défaut si l’utilisateur tape n’importe quoi
    depth_choice = max(1, min(depth_choice, 7))  # borne entre 1 et 7
    self.player2 = AIPlayer(WHITE, depth_choice)
    print("Game started")
    while True:
      if not self.board.get_valid_moves(self.player1.color) and not self.board.get_valid_moves(self.player2.color):
        break
      self.board.display()
      print("Current player :", "Blue" if self.current_player.color == BLACK else "Pink")
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
        print("No valid moves available, skipping turn.")
      else:
        self.board.apply_move(move[0], move[1], self.current_player.color)
      self.current_player = self.player1 if self.current_player == self.player2 else self.player2
    self.board.display()
    black_count, white_count = self.board.count_discs()
    print("Black wins!" if black_count > white_count 
          else "White wins!" if white_count > black_count 
          else "It's a tie!")