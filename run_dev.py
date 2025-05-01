#!/usr/bin/env python3

import argparse
import sys
from terminal_farm.terminal.ui import TerminalUI
from terminal_farm.core.game import GameState
from terminal_farm.web.app import app

def main():
    parser = argparse.ArgumentParser(description='Run Terminal Farm in development mode')
    parser.add_argument('--mode', choices=['terminal', 'web'], default='terminal',
                      help='Choose the game mode (default: terminal)')
    args = parser.parse_args()

    if args.mode == 'terminal':
        game_state = GameState()
        try:
            game_state.load()
        except FileNotFoundError:
            print("No saved game found. Starting a new game...")
        
        ui = TerminalUI(game_state)
        try:
            ui.start_game_loop()
        except KeyboardInterrupt:
            print("\nSaving game and exiting...")
            game_state.save()
            sys.exit(0)
    else:
        print("Starting web server...")
        print("Open your browser and navigate to http://localhost:5000")
        app.run(debug=True)

if __name__ == '__main__':
    main() 