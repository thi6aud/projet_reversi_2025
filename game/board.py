EMPTY = 0
BLACK = 1
WHITE = -1

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),           (0, 1),
              (1, -1),  (1, 0),  (1, 1)]

class Board:
  def __init__(self):
    self.grid = [[EMPTY for _ in range(8)] for _ in range(8)]
    self._init_start_position()
  
  def _init_start_position(self):
    self.grid[3][3] = WHITE
    self.grid[3][4] = BLACK
    self.grid[4][3] = BLACK
    self.grid[4][4] = WHITE

  def count_discs(self):
    black_count = sum(cell == BLACK for row in self.grid for cell in row)
    white_count = sum(cell == WHITE for row in self.grid for cell in row)
    return black_count, white_count
  
  def display(self):
    print("  0 1 2 3 4 5 6 7")
    for i, row in enumerate(self.grid):
      line = ' '.join(self._symbol(cell) for cell in row)
      print(f"{i} {line}")

    black_count, white_count = self.count_discs()
    print(f"Black: {black_count}  White: {white_count}")

  def _symbol(self, cell):
    if cell == BLACK:
      return 'B'
    elif cell == WHITE:
      return 'W'
    else:
      return '.'

  def get_valid_moves(self, player):
    valid_moves = []

    for row in range(8):
      for col in range(8):
        if self.grid[row][col] != EMPTY:
          continue

        for dr, dc in DIRECTIONS:
          r = row + dr
          c = col + dc
          found_opponent = False
          while self.inside(r, c) and self.grid[r][c] != EMPTY and self.grid[r][c] == -player:
            found_opponent = True
            r += dr
            c += dc      
          
          if self.inside(r, c) and self.grid[r][c] == player and found_opponent:
            valid_moves.append((row, col))
            break

    return valid_moves
  
  def inside(self, row, col):
    return 0 <= row < 8 and 0 <= col < 8