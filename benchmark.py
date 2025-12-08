import csv
import time
import sys
from datetime import datetime
from pathlib import Path
from game.board import Board, BLUE, PINK
from game.player import AIPlayer, RandomAIPlayer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

class BenchmarkGame:
    """Lance une partie silencieusement (sans affichage) et retourne les statistiques"""
    
    def __init__(self, player1, player2):
        self.board = Board()
        self.player1 = player1
        self.player2 = player2
        self.current_player = self.player1
        self.player1_time = 0
        self.player1_moves = 0
        self.player2_time = 0
        self.player2_moves = 0
    
    def run(self):
        """Lance la partie et retourne les statistiques"""
        while True:
            if not self.board.get_valid_moves(self.player1.color) and not self.board.get_valid_moves(self.player2.color):
                break
            
            valid_moves = self.board.get_valid_moves(self.current_player.color)
            if not valid_moves:
                # Passer le tour
                self.current_player = self.player1 if self.current_player == self.player2 else self.player2
                continue
            
            # Mesurer le temps du mouvement
            start = time.time()
            move = self.current_player.get_move(self.board)
            elapsed = time.time() - start
            
            if self.current_player == self.player1:
                self.player1_time += elapsed
                self.player1_moves += 1
            else:
                self.player2_time += elapsed
                self.player2_moves += 1
            
            if move is not None:
                self.board.apply_move(move[0], move[1], self.current_player.color)
            
            # Alterner les joueurs
            self.current_player = self.player1 if self.current_player == self.player2 else self.player2
        
        blue_count, pink_count = self.board.count_discs()
        
        # Déterminer le gagnant
        if blue_count > pink_count:
            winner = "BLUE"
            winner_score = blue_count
            loser_score = pink_count
        elif pink_count > blue_count:
            winner = "PINK"
            winner_score = pink_count
            loser_score = blue_count
        else:
            winner = "TIE"
            winner_score = blue_count
            loser_score = pink_count
        
        return {
            'timestamp': datetime.now().isoformat(),
            'player1_type': self._get_player_type(self.player1),
            'player1_depth': getattr(self.player1, 'depth', '-'),
            'player2_type': self._get_player_type(self.player2),
            'player2_depth': getattr(self.player2, 'depth', '-'),
            'winner': winner,
            'blue_score': blue_count,
            'pink_score': pink_count,
            'winner_score': winner_score,
            'loser_score': loser_score,
            'player1_total_time': round(self.player1_time, 3),
            'player1_moves': self.player1_moves,
            'player1_avg_time_ms': round((self.player1_time / self.player1_moves * 1000) if self.player1_moves > 0 else 0, 1),
            'player2_total_time': round(self.player2_time, 3),
            'player2_moves': self.player2_moves,
            'player2_avg_time_ms': round((self.player2_time / self.player2_moves * 1000) if self.player2_moves > 0 else 0, 1),
        }
    
    @staticmethod
    def _get_player_type(player):
        if isinstance(player, AIPlayer):
            return "AIPlayer"
        elif isinstance(player, RandomAIPlayer):
            return "RandomAI"
        else:
            return "Human"


class Benchmark:
    """Gestionnaire des batteries de tests"""
    
    def __init__(self, output_file="benchmark_results.csv"):
        self.output_file = Path(output_file)
        self.results = []
    
    def run_batch(self, num_games, player1_config, player2_config, batch_name=""):
        """
        Lance une batterie de parties
        
        player1_config: dict avec 'type' et optionnellement 'depth'
        player2_config: dict avec 'type' et optionnellement 'depth'
        """
        console.print(f"\n[bold cyan]Lancement de la batterie : {batch_name}[/bold cyan]")
        console.print(f"Configuration : {self._describe_config(player1_config)} vs {self._describe_config(player2_config)}")
        console.print(f"Nombre de parties : {num_games}\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Exécution...", total=num_games)
            
            for i in range(num_games):
                player1 = self._create_player(player1_config, BLUE)
                player2 = self._create_player(player2_config, PINK)
                
                game = BenchmarkGame(player1, player2)
                result = game.run()
                self.results.append(result)
                
                progress.update(task, advance=1)
        
        self._display_batch_summary(self.results[-num_games:], batch_name)
    
    def run_multi_batch(self, num_games_per_batch, configs):
        """
        Lance plusieurs batteries avec différentes configurations
        
        configs: liste de tuples (player1_config, player2_config, batch_name)
        """
        for player1_config, player2_config, batch_name in configs:
            self.run_batch(num_games_per_batch, player1_config, player2_config, batch_name)
    
    def save_results(self):
        """Sauvegarde les résultats en CSV"""
        if not self.results:
            console.print("[yellow]Aucun résultat à sauvegarder[/yellow]")
            return
        
        fieldnames = list(self.results[0].keys())
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        console.print(f"\n[bold green]✓ Résultats sauvegardés dans : {self.output_file.absolute()}[/bold green]")
        console.print(f"[dim]Nombre de parties : {len(self.results)}[/dim]")
    
    @staticmethod
    def _describe_config(config):
        """Retourne une description lisible de la configuration"""
        player_type = config.get('type', 'Unknown')
        depth = config.get('depth', '')
        if depth:
            return f"{player_type}(depth={depth})"
        return player_type
    
    @staticmethod
    def _create_player(config, color):
        """Crée un joueur à partir de la configuration"""
        player_type = config.get('type', 'RandomAI')
        depth = config.get('depth', 4)
        
        if player_type == 'AI':
            return AIPlayer(color, depth=depth)
        else:  # RandomAI par défaut
            return RandomAIPlayer(color)
    
    @staticmethod
    def _display_batch_summary(results, batch_name):
        """Affiche un résumé des résultats de la batterie"""
        if not results:
            return
        
        blue_wins = sum(1 for r in results if r['winner'] == 'BLUE')
        pink_wins = sum(1 for r in results if r['winner'] == 'PINK')
        ties = sum(1 for r in results if r['winner'] == 'TIE')
        
        avg_blue_score = sum(r['blue_score'] for r in results) / len(results)
        avg_pink_score = sum(r['pink_score'] for r in results) / len(results)
        
        table = Table(title=f"Résumé : {batch_name}")
        table.add_column("Statistique", style="cyan")
        table.add_column("Valeur", style="magenta")
        
        table.add_row("Total parties", str(len(results)))
        table.add_row("Victoires BLUE", f"{blue_wins} ({blue_wins/len(results)*100:.1f}%)")
        table.add_row("Victoires PINK", f"{pink_wins} ({pink_wins/len(results)*100:.1f}%)")
        table.add_row("Égalités", f"{ties} ({ties/len(results)*100:.1f}%)")
        table.add_row("Score moyen BLUE", f"{avg_blue_score:.1f}")
        table.add_row("Score moyen PINK", f"{avg_pink_score:.1f}")
        
        console.print(table)


def main():
    """Exemple d'utilisation du benchmark"""
    benchmark = Benchmark(output_file="benchmark_results.csv")
    
    # Configuration des batteries de tests
    configs = [
        # IA depth 3 vs IA depth 3
        (
            {'type': 'AI', 'depth': 3},
            {'type': 'AI', 'depth': 3},
            "IA Depth 3 vs IA Depth 3"
        ),
        # IA depth 4 vs IA depth 3
        (
            {'type': 'AI', 'depth': 4},
            {'type': 'AI', 'depth': 3},
            "IA Depth 4 vs IA Depth 3"
        ),
        # IA depth 5 vs IA depth 4
        (
            {'type': 'AI', 'depth': 5},
            {'type': 'AI', 'depth': 4},
            "IA Depth 5 vs IA Depth 4"
        ),
        # RandomAI vs IA depth 4
        (
            {'type': 'RandomAI'},
            {'type': 'AI', 'depth': 4},
            "RandomAI vs IA Depth 4"
        ),
    ]
    
    # Lance 5 parties par configuration
    benchmark.run_multi_batch(5, configs)
    
    # Sauvegarde les résultats
    benchmark.save_results()


if __name__ == "__main__":
    main()
