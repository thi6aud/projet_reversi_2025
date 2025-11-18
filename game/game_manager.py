from game.board import Board, BLUE, PINK
from game.player import HumanPlayer, AIPlayer
from ui.game_settings import get_gamemode
from ui.game_sign import game_setup
from ui.messages import *

class GameManager:
  def __init__(self):
    self.board = Board()
    self.player1 = None
    self.player2 = None
    self.current_player = None

  def run(self):
    game_setup()
    mode = get_gamemode()
    if mode == 1:
        self.player1 = HumanPlayer(BLUE)
        self.player2 = HumanPlayer(PINK)
    elif mode == 2:
        self.player1 = HumanPlayer(BLUE)
        depth_choice = console.input(MSG_DEPTH_CHOICE)
        try:
            depth_choice = int(depth_choice)
        except ValueError:
          depth_choice = 4
        depth_choice = max(1, min(depth_choice, 5))
        self.player2 = AIPlayer(PINK, depth=depth_choice)
    else:
        depth_choice1 = console.input(MSG_DEPTH_CHOICE_1)
        depth_choice2 = console.input(MSG_DEPTH_CHOICE_2)
        try:
            depth_choice1 = int(depth_choice1)
        except ValueError:
            depth_choice1 = 4
        try:
            depth_choice2 = int(depth_choice2)
        except ValueError:
            depth_choice2 = 4
        depth_choice1 = max(1, min(depth_choice1, 5))
        depth_choice2 = max(1, min(depth_choice2, 5))
        self.player1 = AIPlayer(BLUE, depth=depth_choice1)
        self.player2 = AIPlayer(PINK, depth=depth_choice2)
    self.current_player = self.player1
    console.print(MSG_GAMESTARTED)
    while True:
      if not self.board.get_valid_moves(self.player1.color) and not self.board.get_valid_moves(self.player2.color):
        break
      self.board.display()
      console.print(MSG_BLUETURN if self.current_player.color == BLUE else MSG_PINKTURN)
      if isinstance(self.current_player, AIPlayer):
          stop_event = threading.Event()
          loader_thread = threading.Thread(target=ai_loader, args=(stop_event,))
          loader_thread.start()
          move = self.current_player.get_move(self.board)
          stop_event.set()
          loader_thread.join()
      else:
          move = self.current_player.get_move(self.board)
      if move is None:
        console.print(MSG_SKIPTURN)
      else:
        self.board.apply_move(move[0], move[1], self.current_player.color)
      self.current_player = self.player1 if self.current_player == self.player2 else self.player2
    self.board.display()
    black_count, white_count = self.board.count_discs()
    console.print(MSG_BLUEWINS if black_count > white_count 
          else MSG_PINKWINS if white_count > black_count 
          else MSG_TIE)