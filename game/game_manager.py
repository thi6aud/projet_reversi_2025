import itertools
import threading
import time
from game.board import Board, BLACK, WHITE
from game.player import HumanPlayer, AIPlayer

def show_loader(stop_event):
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
    self.player2 = AIPlayer(WHITE)
    self.current_player = self.player1

  def run(self):
    print("Game started")

    while True:
      if not self.board.get_valid_moves(self.player1.color) and not self.board.get_valid_moves(self.player2.color):
        break
      self.board.display()
      print("Current player :", "Black" if self.current_player.color == BLACK else "White")
      if isinstance(self.current_player, AIPlayer):
          stop_event = threading.Event()
          loader_thread = threading.Thread(target=show_loader, args=(stop_event,))
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