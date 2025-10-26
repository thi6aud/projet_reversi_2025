from game.board import Board, BLACK, WHITE
from game.player import HumanPlayer, AIPlayer

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
      move = self.current_player.get_move(self.board)
      if move is None:
        print("No valid moves available, skipping turn.")
      else:
        self.board.apply_move(move[0], move[1], self.current_player.color)
      self.current_player = self.player1 if self.current_player == self.player2 else self.player2
      if not self.board.get_valid_moves(self.player1.color) and not self.board.get_valid_moves(self.player2.color):
        break
    
    self.board.display()
    black_count, white_count = self.board.count_discs()
    print("Black wins!" if black_count > white_count 
          else "White wins!" if white_count > black_count 
          else "It's a tie!")