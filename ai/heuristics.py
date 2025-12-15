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
    score += mobility_score(board, player) * w.get("mobility", 0)
    score += corner_score(board, player) * w.get("corner", 0)
    score += risk_score(board, player) * w.get("risk", 0)
    score += frontier_score(board, player) * w.get("frontier", 0)
    score += pst_score(board, player) * w.get("pst", 0)
    score += discs_score(board, player) * w.get("discs", 0)
    # Optional advanced signals (default to 0 if not provided)
    score += potential_mobility_score(board, player) * w.get("potential_mobility", 0)
    score += corner_access_score(board, player) * w.get("corner_access", 0)
    score += x_c_penalty_score(board, player) * w.get("x_c_penalty", 0)
    score += edge_stability_score(board, player) * w.get("stability", 0)
    score += parity_score(board) * w.get("parity", 0)
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


# --- Additional feature signals ---

# Potential mobility: empty squares adjacent to opponent discs minus those adjacent to own discs
def potential_mobility_score(board, player):
    adj_opp = set()
    adj_self = set()
    for r in range(8):
        for c in range(8):
            cell = board.grid[r][c]
            if cell == EMPTY:
                continue
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if board.inside(nr, nc) and board.grid[nr][nc] == EMPTY:
                    if cell == -player:
                        adj_opp.add((nr, nc))
                    elif cell == player:
                        adj_self.add((nr, nc))
    return len(adj_opp) - len(adj_self)


# Corner access: bonus if you can play a corner now, malus if opponent can
def corner_access_score(board, player):
    corners = {(0, 0), (0, 7), (7, 0), (7, 7)}
    player_moves = set(board.get_valid_moves(player))
    opponent_moves = set(board.get_valid_moves(-player))
    player_can = any((chr(c + ord("A")), r + 1) in player_moves for r, c in corners)
    opp_can = any((chr(c + ord("A")), r + 1) in opponent_moves for r, c in corners)
    score = 0
    if player_can:
        score += 1
    if opp_can:
        score -= 1
    return score


# X/C-square penalties when the adjacent corner is empty
X_SQUARES = {
    (1, 1): (0, 0),
    (1, 6): (0, 7),
    (6, 1): (7, 0),
    (6, 6): (7, 7),
}

C_SQUARES = {
    (0, 1): (0, 0), (1, 0): (0, 0),
    (0, 6): (0, 7), (1, 7): (0, 7),
    (6, 0): (7, 0), (7, 1): (7, 0),
    (6, 7): (7, 7), (7, 6): (7, 7),
}

def x_c_penalty_score(board, player, x_penalty=20, c_penalty=10):
    score = 0
    for (r, c), (cr, cc) in X_SQUARES.items():
        if board.grid[cr][cc] != EMPTY:
            continue
        cell = board.grid[r][c]
        if cell == player:
            score -= x_penalty
        elif cell == -player:
            score += x_penalty
    for (r, c), (cr, cc) in C_SQUARES.items():
        if board.grid[cr][cc] != EMPTY:
            continue
        cell = board.grid[r][c]
        if cell == player:
            score -= c_penalty
        elif cell == -player:
            score += c_penalty
    return score


# Edge stability: count discs anchored from corners along edges
def edge_stability_score(board, player):
    def count_from_corner(r0, c0, dr, dc, color):
        cnt = 0
        r, c = r0, c0
        while board.inside(r, c) and board.grid[r][c] == color:
            cnt += 1
            r += dr
            c += dc
        return cnt

    score = 0
    corners_dirs = [
        ((0, 0), (0, 1), (1, 0)),
        ((0, 7), (0, -1), (1, 0)),
        ((7, 0), (0, 1), (-1, 0)),
        ((7, 7), (0, -1), (-1, 0)),
    ]
    for (cr, cc), dir_row, dir_col in corners_dirs:
        cell = board.grid[cr][cc]
        if cell == player:
            score += count_from_corner(cr, cc, dir_row[0], dir_row[1], player)
            score += count_from_corner(cr, cc, dir_col[0], dir_col[1], player)
        elif cell == -player:
            score -= count_from_corner(cr, cc, dir_row[0], dir_row[1], -player)
            score -= count_from_corner(cr, cc, dir_col[0], dir_col[1], -player)
    return score


# Parity (advantage if remaining empties is odd for the player to move)
def parity_score(board):
    empties = sum(cell == EMPTY for row in board.grid for cell in row)
    return 1 if (empties % 2 == 1) else -1