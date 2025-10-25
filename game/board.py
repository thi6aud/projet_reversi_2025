from rich.table import Table
from rich.console import Console
from rich import box
console = Console()

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
    table = Table(show_header=True, show_lines=True, box=box.SQUARE)
    
    # colonnes A–H
    table.add_column(" ", justify="center")
    for c in "ABCDEFGH":
        table.add_column(c, justify="center")

    # lignes 1–8
    for i, row in enumerate(self.grid):
        line = [str(i + 1)]
        for cell in row:
            if cell == BLACK:
                line.append("[black]●[/black]")
            elif cell == WHITE:
                line.append("[white]●[/white]")
            else:
                line.append("·")
        table.add_row(*line)

    black_count, white_count = self.count_discs()
    console.print(table)
    console.print(f"[bold white]Black:[/bold white] {black_count} - [bold white]White:[/bold white] {white_count}")

  def get_valid_moves(self, player):
    valid_moves = []

    for row in range(8):
      for col in range(8):
        if self.grid[row][col] != EMPTY:
          continue

        for (dr, dc) in DIRECTIONS:
          r = row + dr
          c = col + dc
          found_opponent = False
          while self.inside(r, c) and self.grid[r][c] != EMPTY and self.grid[r][c] == -player:
            found_opponent = True
            r += dr
            c += dc      
          
          if self.inside(r, c) and self.grid[r][c] == player and found_opponent:
            valid_moves.append((row + 1, chr(col + ord("A"))))
            break

    return valid_moves
  
  def inside(self, row, col):
    return 0 <= row < 8 and 0 <= col < 8
  
  def apply_move(self, row, col, player):
    col = col.upper()
    human_move = (row, col)
    r, c = row - 1, ord(col) - ord("A")

    # Validate using the human-readable form returned by get_valid_moves
    if human_move not in self.get_valid_moves(player):
      return  # invalid move; no change

    # Place the disc
    self.grid[r][c] = player

    # Flip in all directions
    for (dr, dc) in DIRECTIONS:
      rr = r + dr
      cc = c + dc

      if not self.inside(rr, cc) or self.grid[rr][cc] != -player:
        continue

      # Walk over opponent discs
      while self.inside(rr, cc) and self.grid[rr][cc] == -player:
        rr += dr
        cc += dc

      # If we end on our own disc, flip back along the line
      if self.inside(rr, cc) and self.grid[rr][cc] == player:
        rr -= dr
        cc -= dc
        while (rr, cc) != (r, c):
          self.grid[rr][cc] = player
          rr -= dr
          cc -= dc