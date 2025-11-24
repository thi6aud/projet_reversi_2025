import time
import threading
from game.board import Board, BLUE, PINK
from game.player import HumanPlayer, AIPlayer, RandomAIPlayer
from ui.game_settings import get_gamemode
from ui.game_sign import game_setup
from ui.messages import *

class GameManager:
    # Gestion du jeu avec initialisation du plateau et des joueurs,
    # déroulement des tours, gestion des mouvements, et détermination du vainqueur.

    def __init__(self):
        self.board = Board()
        self.player1 = None
        self.player2 = None
        self.current_player = None

    def run(self):
        blueAI_time = 0
        pinkAI_time = 0
        blueAI_moves = 0
        pinkAI_moves = 0
        game_setup()
        mode = get_gamemode()  # Choix du mode de jeu par l'utilisateur, et de la profondeur de l'IA si nécessaire
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
        elif mode == 3:
            # IA random vs humain
            self.player1 = RandomAIPlayer(BLUE)
            self.player2 = HumanPlayer(PINK)
        elif mode == 4:
            # IA random vs IA avec profondeur
            depth_choice = console.input(MSG_DEPTH_CHOICE)
            try:
                depth_choice = int(depth_choice)
            except ValueError:
                depth_choice = 4
            depth_choice = max(1, min(depth_choice, 5))
            self.player1 = RandomAIPlayer(BLUE)
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
                start = time.time()
                move = self.current_player.get_move(self.board)
                elapsed = time.time() - start
                if self.current_player.color == BLUE:
                    blueAI_time += elapsed
                    blueAI_moves += 1
                else:
                    pinkAI_time += elapsed
                    pinkAI_moves += 1
                stop_event.set()
                loader_thread.join()
                console.print(f"[dim]AI thought for {elapsed * 1000:.1f} ms[/dim]")
            else:
                move = self.current_player.get_move(self.board)
            if move is None:
                console.print(MSG_SKIPTURN)
            else:
                self.board.apply_move(move[0], move[1], self.current_player.color)
            self.current_player = self.player1 if self.current_player == self.player2 else self.player2
        self.board.display()
        black_count, white_count = self.board.count_discs()
        if blueAI_moves > 0:
            avg_blue = (blueAI_time / blueAI_moves) * 1000
            console.print(f"[cyan]Temps moyen IA BLUE : {avg_blue:.3f} ms ({blueAI_moves} coups)[/cyan]")

        if pinkAI_moves > 0:
            avg_pink = (pinkAI_time / pinkAI_moves) * 1000
            console.print(f"[magenta]Temps moyen IA PINK : {avg_pink:.3f} ms ({pinkAI_moves} coups)[/magenta]")
        console.print(MSG_BLUEWINS if black_count > white_count
                      else MSG_PINKWINS if white_count > black_count
                      else MSG_TIE)