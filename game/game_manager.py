import time
import threading
from game.board import Board, BLUE, PINK
from game.player import HumanPlayer, AIPlayer, RandomAIPlayer
from ui.game_settings import get_gamemode, get_depth_choice, get_ai_profile_choice
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
        mode = get_gamemode()  # Choix du mode de jeu par l'utilisateur
        if mode == 1:
            self.player1 = HumanPlayer(BLUE)
            self.player2 = HumanPlayer(PINK)
        elif mode == 2:
            self.player1 = HumanPlayer(BLUE)
            depth_choice = get_depth_choice(2)
            self.player2 = AIPlayer(PINK, depth=depth_choice, name=f"AI-D{depth_choice}")
        elif mode == 3:
            # IA random vs humain
            self.player1 = RandomAIPlayer(BLUE)
            self.player2 = HumanPlayer(PINK)
        elif mode == 4:
            # IA random vs IA avec profondeur
            depth_choice = get_depth_choice(2)
            self.player1 = RandomAIPlayer(BLUE, name="RandomAI")
            self.player2 = AIPlayer(PINK, depth=depth_choice, name=f"AI-D{depth_choice}")
        elif mode == 5:
            # AI vs AI avec profils et profondeur
            profile1 = get_ai_profile_choice(1)
            depth1 = get_depth_choice(1)
            self.player1 = AIPlayer(
                BLUE,
                depth=depth1,
                name=f"{profile1['name']} (D{depth1})",
                weights=profile1['weights'],
            )

            profile2 = get_ai_profile_choice(2)
            depth2 = get_depth_choice(2)
            self.player2 = AIPlayer(
                PINK,
                depth=depth2,
                name=f"{profile2['name']} (D{depth2})",
                weights=profile2['weights'],
            )
        else:
            # AI vs AI simple (profondeurs)
            depth_choice1 = get_depth_choice(1)
            depth_choice2 = get_depth_choice(2)
            self.player1 = AIPlayer(BLUE, depth=depth_choice1, name=f"AI-D{depth_choice1}")
            self.player2 = AIPlayer(PINK, depth=depth_choice2, name=f"AI-D{depth_choice2}")
        self.current_player = self.player1
        console.print(MSG_GAMESTARTED)
        while True:
            if not self.board.get_valid_moves(self.player1.color) and not self.board.get_valid_moves(self.player2.color):
                break
            self.board.display()
            player_name = getattr(self.current_player, 'name', None)
            if player_name:
                console.print(f"Current player : [bold bright_cyan]{player_name}[/bold bright_cyan]" if self.current_player.color == BLUE else f"Current player : [bold bright_magenta]{player_name}[/bold bright_magenta]")
            else:
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
                ai_name = getattr(self.current_player, 'name', 'AI')
                console.print(f"[dim]{ai_name} thought for {elapsed * 1000:.1f} ms[/dim]")
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
            console.print(f"[cyan]Temps moyen IA BLUE ({getattr(self.player1,'name','BLUE')}) : {avg_blue:.3f} ms ({blueAI_moves} coups)[/cyan]")

        if pinkAI_moves > 0:
            avg_pink = (pinkAI_time / pinkAI_moves) * 1000
            console.print(f"[magenta]Temps moyen IA PINK ({getattr(self.player2,'name','PINK')}) : {avg_pink:.3f} ms ({pinkAI_moves} coups)[/magenta]")
        
        # Display winner with AI names if applicable
        if black_count > white_count:
            winner_name = getattr(self.player1, 'name', 'Blue')
            console.print(f"[bold bright_cyan]{winner_name} wins![/bold bright_cyan]")
        elif white_count > black_count:
            winner_name = getattr(self.player2, 'name', 'Pink')
            console.print(f"[bold bright_magenta]{winner_name} wins![/bold bright_magenta]")
        else:
            console.print(MSG_TIE)