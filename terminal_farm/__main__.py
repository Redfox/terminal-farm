import sys
from terminal_farm.core.game import GameState
from terminal_farm.terminal.ui import TerminalUI
import time

def main():
    game_state = GameState()
    ui = TerminalUI(game_state)
    
    if not game_state.load():
        print("Starting new game...")
        time.sleep(1)
    
    try:
        ui.start_game_loop()
    except KeyboardInterrupt:
        game_state.save()
        print(f"\nGame saved automatically!")
        sys.exit()

if __name__ == "__main__":
    main() 