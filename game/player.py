import random
from game.board import BLACK, WHITE, EMPTY

class Player:
  def __init__(self, color):
    self.color = color

class HumanPlayer(Player):
  def get_move(self, board):
    valid = board.get_valid_moves(self.color)
    if not valid:
      return None

    while True:
      print("Valid moves:", ", ".join([f"{r}{c}" for r, c in valid]))
      raw = input("Enter your move (row col): ").strip().replace(",", "").replace(" ", "").upper()

      # Handle combined input like "3D"
      if len(raw) == 2 and raw[0].isdigit() and raw[1].isalpha():
          row_part, col_part = raw[0], raw[1]
      elif len(raw) == 3 and raw[:2].isdigit() and raw[2].isalpha():
          row_part, col_part = raw[:2], raw[2]
      else:
          print("Expected format: e.g. 3D or 3 D")
          continue

      # convert row 1–8
      if not row_part.isdigit() or not (1 <= int(row_part) <= 8):
          print("Row must be between 1 and 8.")
          continue
      row = int(row_part)

      # convert col A–H
      if col_part not in "ABCDEFGH":
          print("Column must be between A–H.")
          continue
      col = col_part

      move = (row, col)
      if move not in valid:
          print("Invalid move. Try again.")
          continue

      return move

class AIPlayer(Player):
  def __init__(self, color, depth=1):
    super().__init__(color)
    self.depth = depth

  def get_move(self, board):
    valid_moves = board.get_valid_moves(self.color)
    if not valid_moves:
      return None
    return random.choice(valid_moves)