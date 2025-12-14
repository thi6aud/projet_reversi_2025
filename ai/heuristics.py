from game.board import BLUE, DIRECTIONS, EMPTY
from ai.heuristics_consts import *

# score weighting based on game phase
def game_phase(board):
    count_empty = sum(cell == EMPTY for row in board.grid for cell in row)
    if count_empty > 44:
        return "opening"
    elif count_empty > 20:
        return "midgame"
    else:
        return "endgame"

DEFAULT_WEIGHTS = {
    "opening": {
        "mobility": 1.25,
        "corner": 1.5,
        "risk": 0.75,
        "frontier": 0.75,
        "pst": 1.0,
        "discs": 0.1,
    },
    "midgame": {
        "mobility": 1.25,
        "corner": 1.5,
        "risk": 0.5,
        "frontier": 1.0,
        "pst": 1.0,
        "discs": 0.5,
    },
    "endgame": {
        "mobility": 0.5,
        "corner": 1.25,
        "risk": 0.5,
        "frontier": 0.5,
        "pst": 0.5,
        "discs": 1.5,
    },
}

def evaluate(board, player, weights=None):
    phase = game_phase(board)
    w = (weights or DEFAULT_WEIGHTS).get(phase, DEFAULT_WEIGHTS[phase])
    score = 0
    score += mobility_score(board, player) * w["mobility"]
    score += corner_score(board, player) * w["corner"]
    score += risk_score(board, player) * w["risk"]
    score += frontier_score(board, player) * w["frontier"]
    score += pst_score(board, player) * w["pst"]
    score += discs_score(board, player) * w["discs"]
    return score

def mobility_score(board, player):
    player_valid_moves = board.get_valid_moves(player)
    opponent_valid_moves = board.get_valid_moves(-player)
    player_moves = len(player_valid_moves)
    opponent_moves = len(opponent_valid_moves)
    return player_moves - opponent_moves

def corner_score(board, player):
    score = 0
    for (r, c) in CORNERS:
        if board.grid[r][c] == player:
            score += 25
        elif board.grid[r][c] == -player:
            score -= 25
    return score

def risk_score(board, player):
    score = 0  
    for group in CORNER_GROUPS:
        if board.grid[group[0][0]][group[0][1]] == EMPTY:
            if board.grid[group[1][0]][group[1][1]] == player:
                score += 15
            elif board.grid[group[1][0]][group[1][1]] == -player:
                score -= 15
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
                score += PST[r][c]
            elif board.grid[r][c] == -player:
                score -= PST[r][c]
    return score

def discs_score(board, player):
    discs = board.count_discs()
    return discs[0] - discs[1] if player == BLUE else discs[1] - discs[0]