import random

class Player:
  def __init__(self, color):
    self.color = color

class HumanPlayer(Player):
  def get_move(self, board):
    valid_moves = board.get_valid_moves(self.color)
    if not valid_moves:
      return None

    while True:
      print("Valid moves:", ", ".join([f"{c}{r}" for c, r in valid_moves]))
      raw = input("Enter your move (colrow): ").strip().replace(",", "").replace(" ", "").upper()

      # Gère une saisie comme "D3"
      if len(raw) == 2 and raw[0].isalpha() and raw[1].isdigit():
          col_part, row_part = raw[0], raw[1]
      else:
          print("Expected format: e.g. D3")
          continue

      # Ligne 1–8
      if not row_part.isdigit() or not (1 <= int(row_part) <= 8):
          print("Row must be between 1 and 8.")
          continue
      row = int(row_part)

      # Colonne A–H
      if col_part not in "ABCDEFGH":
          print("Column must be between A–H.")
          continue
      col = col_part

      move = (col, row)
      if move not in valid_moves:
          print("Invalid move. Try again.")
          continue

      return move

class AIPlayer(Player):
  def __init__(self, color):
    super().__init__(color)

  def get_move(self, board):
    valid_moves = board.get_valid_moves(self.color)
    if not valid_moves:
      return None
    return random.choice(valid_moves)