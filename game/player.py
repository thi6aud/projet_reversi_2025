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
      try:
        print(f"Valid moves: {valid}")
        raw = input("Enter your move (row col): ").strip()
        parts = raw.split()
        if len(parts) != 2:
          print("Expected format: two integers separated by a space (e.g. 2 3)")
          continue
        row, col = int(parts[0]), int(parts[1])
        if not (0 <= row < 8 and 0 <= col < 8):
          print("Coordinates must be between 0 and 7.")
          continue
        if (row, col) not in valid:
          print("Invalid move. Try again.")
          continue
        return (row, col)
      except ValueError:
        print("Invalid input: please enter two integers (e.g. 2 3)")
        continue
      except (KeyboardInterrupt, EOFError):
        print("\nInterruption detected: skipping turn.")
        return None

class AIPlayer(Player):
  def __init__(self, color, depth=1):
    super().__init__(color)
    self.depth = depth

  def get_move(self, board):
    valid_moves = board.get_valid_moves(self.color)
    if not valid_moves:
      return None
    return valid_moves[random.randint(0, len(valid_moves) - 1)]