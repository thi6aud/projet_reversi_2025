from rich.console import Console
from ui.messages import print_slowly

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