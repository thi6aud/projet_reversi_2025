from ai.heuristics import evaluate
from ai.heuristics_consts import *

def choose_move(board, player, depth):
    valid_moves = board.get_valid_moves(player)
    if not valid_moves:
        return None
    def evaluate_move(move):
        flipped = board.make_move(move, player)
        score = -search(board, -player, depth - 1)
        board.undo_move(move, flipped, player)
        return score
    best_move = max(valid_moves, key=evaluate_move)
    return best_move

TT = {}

def search(board, player, depth, alpha=float('-inf'), beta=float('inf')):
  key = (tuple(map(tuple, board.grid)), player, depth)
  if key in TT:
    return TT[key]
  best_score = float('-inf')
  if board.is_terminal():
    return board.score(player)
  if depth == 0:
    return evaluate(board, player)
  valid_moves = board.get_valid_moves(player)
  if not valid_moves:
    return -search(board, -player, depth, -beta, -alpha)
  def score(move):
    return quick_eval(move)
  valid_moves.sort(key=score, reverse=True)
  for move in valid_moves:
    flipped = board.make_move(move, player)
    child_score = -search(board, -player, depth-1, -beta, -alpha)
    board.undo_move(move, flipped, player)

    best_score = max(best_score, child_score)
    alpha = max(alpha, child_score)
    if alpha >= beta:
        break
  TT[key] = best_score
  return best_score

def quick_eval(move):
    row, col = move

    # Normaliser la colonne (lettre ou chiffre en string)
    if isinstance(col, str):
        col_str = col.strip().upper()
        if len(col_str) == 1 and col_str.isalpha():
            col = ord(col_str) - ord('A')   # 'A'->0, 'B'->1, ...
        elif col_str.isdigit():
            col = int(col_str)
    if not isinstance(col, int):
        col = 0  # valeur de secours

    # Normaliser la ligne (string -> int)
    if isinstance(row, str):
        row_str = row.strip()
        if row_str.isdigit():
            row = int(row_str)

    if isinstance(row, int) and 1 <= row <= 8:
        row_idx = row - 1
    elif isinstance(row, int):
        row_idx = row
    else:
        row_idx = 0  # valeur de secours

    # Bornage 0–7
    row_idx = max(0, min(7, row_idx))
    col = max(0, min(7, col))

    return PST[row_idx][col]