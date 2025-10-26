from game.board import BLACK, DIRECTIONS, EMPTY

pst = [
  [20, -3, 11, 8, 8, 11, -3, 20],
  [ -3, -7, -4, 1, 1, -4, -7, -3],
  [11, -4, 2, 2, 2, 2, -4, 11],
  [8, 1, 2, 0, 0, 2, 1, 8],
  [8, 1, 2, 0, 0, 2, 1, 8],
  [11, -4, 2, 2, 2, 2, -4, 11],
  [-3, -7, -4, 1, 1, -4, -7, -3],
  [20, -3, 11, 8, 8, 11, -3, 20]
    ]

corner_group_1 = [(0, 0), (1, 1), (0, 1), (1, 0)]
corner_group_2 = [(0, 7), (1, 6), (0, 6), (1, 7)]
corner_group_3 = [(7, 0), (6, 1), (6, 0), (7, 1)]
corner_group_4 = [(7, 7), (6, 6), (6, 7), (7, 6)]

def game_phase(board):
    count_empty = sum(cell == EMPTY for row in board.grid for cell in row)
    if count_empty > 44:
        return "opening"
    elif count_empty > 20:
        return "midgame"
    else:
        return "endgame"

def opening_game_evaluation(board, player):
    score = 0
    score += mobility_score(board, player) * 1.25
    score += corner_score(board, player) * 1.5
    score += risk_score(board, player) * 0.75
    score += frontier_score(board, player) * 0.75
    score += pst_score(board, player) * 1.0
    score += discs_score(board, player) * 0.1
    return score

def midgame_evaluation(board, player):
    score = 0
    score += mobility_score(board, player) * 1.25
    score += corner_score(board, player) * 1.5
    score += risk_score(board, player) * 0.5
    score += frontier_score(board, player) * 1.0
    score += pst_score(board, player) * 1.0
    score += discs_score(board, player) * 0.5
    return score

def endgame_evaluation(board, player):
    score = 0
    score += mobility_score(board, player) * 0.5
    score += corner_score(board, player) * 1.25
    score += risk_score(board, player) * 0.5
    score += frontier_score(board, player) * 0.5
    score += pst_score(board, player) * 0.5
    score += discs_score(board, player) * 1.5
    return score

def evaluate(board, player):
    phase = game_phase(board)
    if phase == "opening":
        return opening_game_evaluation(board, player)
    elif phase == "midgame":
        return midgame_evaluation(board, player)
    else:
        return endgame_evaluation(board, player)

def mobility_score(board, player):
    player_valid_moves = board.get_valid_moves(player)
    opponent_valid_moves = board.get_valid_moves(-player)
    player_moves = len(player_valid_moves)
    opponent_moves = len(opponent_valid_moves)
    return player_moves - opponent_moves

def corner_score(board, player):
    corner_pos = [(0, 0), (0, 7), (7, 0), (7, 7)]
    score = 0
    for (r, c) in corner_pos:
      if board.grid[r][c] == player:
          score += 25
      elif board.grid[r][c] == -player:
          score -= 25
    return score

def risk_score(board, player):
  score = 0
  corner_groups = [corner_group_1, corner_group_2, corner_group_3, corner_group_4]
  
  for group in corner_groups:
      if board.grid[group[0][0]][group[0][1]] == EMPTY:
          if board.grid[group[1][0]][group[1][1]] == player:
              score -= 15
          elif board.grid[group[1][0]][group[1][1]] == -player:
              score += 15
  return score

def frontier_score(board, player):
    score = 0
    player_tiles = [(r, c) for r in range(8) for c in range(8) if board.grid[r][c] == player]
    opponent_tiles = [(r, c) for r in range(8) for c in range(8) if board.grid[r][c] == -player]
    for (r, c) in player_tiles:
        for (dr, dc) in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if board.inside(nr, nc) and board.grid[nr][nc] == EMPTY:
                score -= 1
                break
    for (r, c) in opponent_tiles:
        for (dr, dc) in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if board.inside(nr, nc) and board.grid[nr][nc] == EMPTY:
                score += 1
                break
    return score

def pst_score(board, player):
    score = 0
    for r in range(8):
        for c in range(8):
            if board.grid[r][c] == player:
                score += pst[r][c]
            elif board.grid[r][c] == -player:
                score -= pst[r][c]
    return score

def discs_score(board, player):
    discs = board.count_discs()
    return discs[0] - discs[1] if player == BLACK else discs[1] - discs[0]