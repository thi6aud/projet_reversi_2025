from game.board import Board, BLACK

if __name__ == "__main__":
    b = Board()
    b.display()
    print("Valid moves for BLACK:", b.get_valid_moves(BLACK))