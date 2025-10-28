from ai.heuristics import evaluate

def choose_move(board, player, depth):
    valid_moves = board.get_valid_moves(player)
    if not valid_moves:
        return None
    def evaluate_move(move):
        clone = board.clone()
        clone.apply_move(move[0], move[1], player)
        return -search(clone, -player, depth - 1)
    best_move = max(valid_moves, key=evaluate_move)
    return best_move

def search(board, player, depth, alpha=float('-inf'), beta=float('inf')):
  best_score = float('-inf')
  if board.is_terminal():
    return board.score(player)
  if depth == 0:
    return evaluate(board, player)
  valid_moves = board.get_valid_moves(player)
  if not valid_moves:
    return -search(board, -player, depth, -beta, -alpha)
  def score(move):
    return quick_eval(board, move, player)
  valid_moves.sort(key=score, reverse=True)
  for move in valid_moves:
    clone_board = board.clone()
    clone_board.apply_move(move[0], move[1], player)
    child_score = -search(clone_board, -player, depth-1, -beta, -alpha)
    best_score = max(best_score, child_score)
    alpha = max(alpha, child_score)
    if alpha >= beta:
      break
  return best_score

def quick_eval(board, move, player):
    clone = board.clone()
    clone.apply_move(move[0], move[1], player)
    return evaluate(clone, player)
