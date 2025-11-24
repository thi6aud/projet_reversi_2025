from rich.table import Table # Bibliothèque rich pour l'aspect visuel du plateau
from rich.console import Console
from rich import box

console = Console()

EMPTY = 0
BLUE = 1
PINK = -1

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),           (0, 1),
              (1, -1),  (1, 0),  (1, 1)]

class Board: # Initialisation du plateau du début de partie avec les 4 pions centraux
  def __init__(self):
    # grid[row][col]  -> row/ligne d'abord, col/colonne ensuite
    self.grid = [[EMPTY for _ in range(8)] for _ in range(8)]
    self._init_start_position()
  
  def _init_start_position(self):
    self.grid[3][3] = PINK
    self.grid[3][4] = BLUE
    self.grid[4][3] = BLUE
    self.grid[4][4] = PINK

  def count_discs(self):
    blue_count = sum(cell == BLUE for row in self.grid for cell in row)
    pink_count = sum(cell == PINK for row in self.grid for cell in row)
    return blue_count, pink_count

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
            if cell == BLUE:
                line.append("[bright_cyan]●[/bright_cyan]")
            elif cell == PINK:
                line.append("[bright_magenta]●[/bright_magenta]")
            else:
                line.append("·")
        table.add_row(*line)

    blue_count, pink_count = self.count_discs()
    console.print(table)
    console.print(f"[bold white]Blue:[/bold white] [bright_cyan]{blue_count}[/bright_cyan] - [bold white]Pink:[/bold white] [bright_magenta]{pink_count}[/bright_magenta]")

  def get_valid_moves(self, player): # Vérifie les mouvement possibles et proposent ceux qui permettent de capturer au moins un jeton adverse.
    valid_moves = []

    for row in range(8):
      for col in range(8):
        if self.grid[row][col] != EMPTY:
          continue

        for (dr, dc) in DIRECTIONS:
          r = row + dr
          c = col + dc
          found_opponent = False

          while self.inside(r, c) and self.grid[r][c] == -player:
            found_opponent = True
            r += dr
            c += dc

          if self.inside(r, c) and self.grid[r][c] == player and found_opponent:
            # exposer au format humain (col, row) -> ex: ("D", 3)
            valid_moves.append((chr(col + ord("A")), row + 1))
            break

    return valid_moves

  def inside(self, row, col):
    return 0 <= row < 8 and 0 <= col < 8

  def apply_move(self, col, row, player): #Prend en compte le choix du joueur, vérifie s’il est parmi les coups valides place le jeton et retourne les jetons capturés 
    """
    Reçoit un coup au format humain (col lettre A–H, row 1–8), ex: ('D', 3).
    À l'intérieur on travaille en (row, col) 0-indexés.
    """
    col = col.upper()
    human_move = (col, row)

    # Vérifier que le coup est légal au format (col, row)
    if human_move not in self.get_valid_moves(player):
      return  # coup invalide; pas de changement

    # Conversion vers indices 0-based (row, col)
    r = row - 1
    c = ord(col) - ord("A")

    # Poser le pion
    self.grid[r][c] = player

    # Retourner dans toutes les directions (dr, dc)
    for (dr, dc) in DIRECTIONS:
      rr = r + dr
      cc = c + dc

      if not self.inside(rr, cc) or self.grid[rr][cc] != -player:
        continue

      # Avancer sur les pions adverses
      while self.inside(rr, cc) and self.grid[rr][cc] == -player:
        rr += dr
        cc += dc

      # Si on retombe sur un de nos pions, on retourne en arrière
      if self.inside(rr, cc) and self.grid[rr][cc] == player:
        rr -= dr
        cc -= dc
        while (rr, cc) != (r, c):
          self.grid[rr][cc] = player
          rr -= dr
          cc -= dc

  def clone(self):
      clone_board = Board()
      for row in range(8):
        for col in range(8):
          clone_board.grid[row][col] = self.grid[row][col]
      return clone_board

  def is_terminal(self): #vérifie s’il reste des coups valides pour les 2 joueurs, renvoie True si aucun coups possibles donc fin de partie 
      return not self.get_valid_moves(BLUE) and not self.get_valid_moves(PINK)

  def score(self, player): # calcul le score du joueur = la différence entre les jetons du joueur moins ceux de l’adversaire 

    blue_count, pink_count = self.count_discs()
    return (blue_count - pink_count) if player == BLUE else (pink_count - blue_count)