from rich.console import Console
from ai.ai_profiles import AI_PROFILES

console = Console()

def get_gamemode():
    mode = console.input(
        "\nSelect mode:\n"
        "1. Human vs Human\n"
        "2. Human vs AI\n"
        "3. IA random vs Human\n"
        "4. IA random vs AI\n"
        "5. AI vs AI\n\n"
        "Enter choice (1-5): "
    )
    try:
        mode = int(mode)
    except ValueError:
        mode = 1
    if mode in [1, 2, 3, 4, 5]:
        return mode
    return 1

def get_depth_choice(player_num):
    console.print(f"\n[bold cyan]Configuration de l'IA {player_num} : Profondeur[/bold cyan]")
    console.print("  1  2  3  4  5")
    while True:
        try:
            depth = int(input(f"Profondeur de l'IA {player_num} (1-5) : ").strip())
        except ValueError:
            console.print("[yellow]Veuillez entrer un nombre[/yellow]")
            continue
        if 1 <= depth <= 5:
            return depth
        console.print("[yellow]Veuillez entrer une valeur entre 1 et 5[/yellow]")

def get_ai_profile_choice(player_num):
    console.print(f"\n[bold cyan]Configuration de l'IA {player_num} : Choix du Profil[/bold cyan]")
    for i, profile in enumerate(AI_PROFILES, start=1):
        console.print(f"  [bold]{i} - {profile['name']}[/bold] [dim]({profile.get('description','')})[/dim]")
    while True:
        try:
            choice = int(input("Entrez le numéro du profil : ").strip())
        except ValueError:
            console.print("[yellow]Veuillez entrer un nombre[/yellow]")
            continue
        idx = choice - 1
        if 0 <= idx < len(AI_PROFILES):
            return AI_PROFILES[idx]
        console.print(f"[yellow]Veuillez entrer un numéro entre 1 et {len(AI_PROFILES)}[/yellow]")