import random
from ai.minimax import choose_move
from rich.console import Console
from game.messages import *
from game.board import BLUE, PINK

console = Console()

class Player:
  def __init__(self, color):
    self.color = color

class HumanPlayer(Player):
  def get_move(self, board):
    valid_moves = board.get_valid_moves(self.color)
    if not valid_moves:
      return None

    while True:
      message_color = "[bold bright_cyan]" if self.color == BLUE else "[bold bright_magenta]"
      console.print(f"{message_color}{MSG_VALIDMOVES}[/]{message_color}", ", ".join([f"{c}{r}" for c, r in valid_moves]))
      raw = input(MSG_ENTERMOVE).strip().replace(",", "").replace(" ", "").upper()

      # Gère une saisie comme "D3"
      if len(raw) == 2 and raw[0].isalpha() and raw[1].isdigit():
          col_part, row_part = raw[0], raw[1]
      else:
          console.print(f"{ERROR_START}{ERR_EXPECTEDFORMAT}{ERROR_END}")
          continue

      # Ligne 1–8
      if row_part not in ROWS:
          console.print(f"{ERROR_START}{ERR_ROWRANGE}{ERROR_END}")
          continue
      row = int(row_part)

      # Colonne A–H
      if col_part not in COLS:
          console.print(f"{ERROR_START}{ERR_COLRANGE}{ERROR_END}")
          continue
      col = col_part

      move = (col, row)
      if move not in valid_moves:
          console.print(f"{ERROR_START}{ERR_INVALIDMOVE}{ERROR_END}")
          continue

      return move

class AIPlayer(Player):
  def __init__(self, color, depth=4):
    super().__init__(color)
    self.depth = depth

  def get_move(self, board):
    valid_moves = board.get_valid_moves(self.color)
    if not valid_moves:
      return None
    return choose_move(board, self.color, depth=self.depth)