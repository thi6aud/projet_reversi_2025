#!/usr/bin/env python3
"""Teste speed à depth 4 et affiche stats détaillées."""

import time
from game.board import Board
from game.player import Player
from ai.minimax import search, TT

DEPTH = 4

board = Board()
player = 1
move_count = 0
total_time = 0

print(f"Teste 1 partie complète à depth={DEPTH}\n")

while True:
    valid = board.get_valid_moves(player)
    if not valid:
        player = -player
        valid = board.get_valid_moves(player)
    if not valid:
        break
    
    move_count += 1
    
    # Chrono + search
    start = time.time()
    best_score = float('-inf')
    best_move = None
    for move in valid:
        flipped = board.make_move(move, player)
        score = -search(board, -player, DEPTH - 1)
        board.undo_move(move, flipped, player)
        if score > best_score:
            best_score = score
            best_move = move
    elapsed = time.time() - start
    total_time += elapsed
    
    tt_size = len(TT)
    
    print(f"Coup {move_count:2d}: {elapsed:.3f}s | TT={tt_size:6d} | Score={best_score:6.0f}")
    
    # Jouer le coup
    board.make_move(best_move, player)
    player = -player

print(f"\nTotal: {move_count} coups en {total_time:.2f}s (avg {total_time/move_count:.3f}s/coup)")
