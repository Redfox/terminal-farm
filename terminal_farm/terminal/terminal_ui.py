import os
import time
from typing import List, Optional
from ..core.game import Game
from ..core.models import Crop

class TerminalUI:
    def __init__(self):
        self.game = Game.load()
        self.messages: List[str] = []
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_messages(self):
        if self.messages:
            print("\n=== Messages ===")
            for msg in self.messages:
                print(f"- {msg}")
            print("===============\n")
            self.messages = []
    
    def display_status(self):
        print("\n=== Farm Status ===")
        print(f"Day: {self.game.time_system.day}")
        print(f"Time: {self.game.day_cycle.get_current_part().capitalize()}")
        print(f"Weather: {self.game.weather_system.get_weather().capitalize()}")
        print(f"Money: ${self.game.player.money}")
        print(f"Stamina: {'❤' * int(self.game.player.stamina)}")
        print("==================\n")
    
    def display_farm(self):
        print("\n=== Your Farm ===")
        for i, plot in enumerate(self.game.farm.plots):
            status = "Empty"
            if not plot.is_empty:
                progress = int(plot.growth_progress * 10)
                status = f"{plot.crop.name} [{progress}/10]"
            print(f"Plot {i + 1}: {status}")
        print("================\n")
    
    def display_available_crops(self):
        print("\n=== Available Crops ===")
        for crop in self.game.crop_system.get_unlocked_crops():
            cost = crop.cost * 2 if self.game.market_inflated else crop.cost
            print(f"{crop.name}: ${cost} (Growth: {crop.growth_time}s, Value: ${crop.value})")
        print("======================\n")
    
    def get_user_input(self, prompt: str) -> str:
        return input(prompt).strip().lower()
    
    def handle_plant(self):
        self.display_available_crops()
        crop_name = self.get_user_input("Enter crop name to plant: ")
        plot_index = self.get_user_input("Enter plot number (1-9): ")
        
        try:
            plot_index = int(plot_index) - 1
            if 0 <= plot_index < len(self.game.farm.plots):
                message = self.game.plant_crop(plot_index, crop_name)
                self.messages.append(message)
            else:
                self.messages.append("Invalid plot number!")
        except ValueError:
            self.messages.append("Please enter a valid number!")
    
    def handle_harvest(self):
        message = self.game.harvest_crops()
        self.messages.append(message)
    
    def handle_sleep(self):
        message = self.game.sleep()
        self.messages.append(message)
    
    def handle_save(self):
        message = self.game.save()
        self.messages.append(message)
    
    def handle_quit(self):
        self.handle_save()
        print("\nThanks for playing! Goodbye!")
        time.sleep(1)
        return True
    
    def display_menu(self):
        print("\n=== Menu ===")
        print("1. Plant crops")
        print("2. Harvest crops")
        print("3. Sleep")
        print("4. Save game")
        print("5. Quit")
        print("===========\n")
    
    def run(self):
        while True:
            self.clear_screen()
            self.display_status()
            self.display_farm()
            self.display_messages()
            self.display_menu()
            
            choice = self.get_user_input("Enter your choice (1-5): ")
            
            if choice == "1":
                self.handle_plant()
            elif choice == "2":
                self.handle_harvest()
            elif choice == "3":
                self.handle_sleep()
            elif choice == "4":
                self.handle_save()
            elif choice == "5":
                if self.handle_quit():
                    break
            else:
                self.messages.append("Invalid choice! Please enter a number between 1 and 5.")
            
            # Update game state
            self.messages.extend(self.game.update())
            
            # Add a small delay to make the game feel more natural
            time.sleep(0.5)

if __name__ == "__main__":
    ui = TerminalUI()
    ui.run() 