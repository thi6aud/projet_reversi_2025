from ai.heuristics import evaluate, game_phase
from ai.heuristics_consts import *
import random
from collections import OrderedDict

# Transposition table with size limit to avoid unbounded memory growth
MAX_TT_ENTRIES = 50000

def choose_move(board, player, depth, weights=None):
  valid_moves = board.get_valid_moves(player)
  if not valid_moves:
    return None

  def evaluate_move(move):
    flipped = board.make_move(move, player)
    score = -search(board, -player, depth - 1, weights=weights)
    board.undo_move(move, flipped, player)
    return score

  # Évaluer tous les coups
  move_scores = [(move, evaluate_move(move)) for move in valid_moves]

  # Trouver le meilleur score
  best_score = max(score for _, score in move_scores)

  # Sélectionner tous les coups avec le meilleur score
  best_moves = [move for move, score in move_scores if score == best_score]

  # Si plusieurs coups ont le même score, en choisir un aléatoirement
  return random.choice(best_moves)

TT = OrderedDict()

def search(board, player, depth, alpha=float('-inf'), beta=float('inf'), weights=None):
  # Only build a TT key for depths >= 3 to reduce allocation overhead
  key = None
  if depth >= 3:
    key = (tuple(map(tuple, board.grid)), player, depth, id(weights) if weights is not None else None)
    if key in TT:
      return TT[key]
  best_score = float('-inf')
  if board.is_terminal():
    return board.score(player)
  if depth == 0:
    return evaluate(board, player, weights=weights)
  valid_moves = board.get_valid_moves(player)
  if not valid_moves:
    return -search(board, -player, depth, -beta, -alpha, weights=weights)
  
  # Tri des coups: seulement en midgame et profondeur >= 4
  phase = game_phase(board)
  if depth >= 4 and phase == 'midgame':
    scored_moves = [(move, quick_eval(move, board, player)) for move in valid_moves]
    scored_moves.sort(key=lambda item: item[1], reverse=True)
    valid_moves = [move for move, _ in scored_moves]
  for move in valid_moves:
    flipped = board.make_move(move, player)
    child_score = -search(board, -player, depth-1, -beta, -alpha, weights=weights)
    board.undo_move(move, flipped, player)

    best_score = max(best_score, child_score)
    alpha = max(alpha, child_score)
    if alpha >= beta:
        break
  # store in TT if we constructed a key
  if key is not None:
    TT[key] = best_score
    # maintain size limit
    if len(TT) > MAX_TT_ENTRIES:
      TT.popitem(last=False)
  return best_score

def quick_eval(move, board=None, player=None):
    """
    Évalue un coup pour le tri des mouvements (move ordering).
    Basé sur:
    1. Nombre de disques retournés (principal)
    2. Control des coins (très importants en Othello)
    3. Pénalité pour les carrés dangereux
    
    Cette heuristique est bien plus pertinente que PST pour Othello.
    """
    row, col = move
    
    # Normaliser la colonne
    if isinstance(col, str):
        col_str = col.strip().upper()
        if len(col_str) == 1 and col_str.isalpha():
            col = ord(col_str) - ord('A')
        elif col_str.isdigit():
            col = int(col_str)
    if not isinstance(col, int):
        col = 0

    # Normaliser la ligne
    if isinstance(row, str):
        row_str = row.strip()
        if row_str.isdigit():
            row = int(row_str)

    if isinstance(row, int) and 1 <= row <= 8:
        row_idx = row - 1
    elif isinstance(row, int):
        row_idx = row
    else:
        row_idx = 0

    row_idx = max(0, min(7, row_idx))
    col = max(0, min(7, col))

    score = 0

    # 1. Bonus pour les coins (très importants en Othello)
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    if (row_idx, col) in corners:
        score += 1000

    # 2. Pénalité pour les carrés dangereux (adjacents aux coins vides)
    # Ces carrés donnent à l'adversaire accès aux coins
    dangerous = [
        (0, 1), (1, 0), (1, 1),  # autour du coin (0,0)
        (0, 6), (1, 6), (1, 7),  # autour du coin (0,7)
        (6, 0), (6, 1), (7, 1),  # autour du coin (7,0)
        (6, 6), (6, 7), (7, 6),  # autour du coin (7,7)
    ]
    if (row_idx, col) in dangerous:
        score -= 500

    # 3. Bonus pour les bords (X-squares) - bonne stabilité
    edges = [(i, j) for i in range(8) for j in range(8) if i in (0, 7) or j in (0, 7)]
    if (row_idx, col) in edges and (row_idx, col) not in corners and (row_idx, col) not in dangerous:
        score += 50

    # 4. Nombre de disques retournés (si board et player fournis)
    if board is not None and player is not None:
        flipped = board.make_move((row, col), player)
        score += len(flipped) * 10  # Bonus proportionnel au nombre de disques retournés
        board.undo_move((row, col), flipped, player)

    return score