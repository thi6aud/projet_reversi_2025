from rich.console import Console

console = Console()

def get_gamemode():
  mode = console.input("Select mode:\n1. Human vs Human\n2. Human vs AI\n3. AI vs AI\nEnter choice (1-3): ")
  try:
      mode = int(mode)
  except ValueError:
      mode = 1
  if mode == 1:
    return 1
  elif mode == 2:
    return 2
  elif mode == 3:
    return 3
  return 1