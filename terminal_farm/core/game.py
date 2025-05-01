import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from .models import (
    Player, FarmSystem, CropSystem, WeatherSystem, TimeSystem, 
    EventSystem, DayCycleSystem, ISerializable
)

class Game(ISerializable):
    SAVE_FILE = "save.json"
    
    def __init__(self):
        self.player = Player()
        self.farm = FarmSystem()
        self.crop_system = CropSystem()
        self.weather_system = WeatherSystem()
        self.time_system = TimeSystem()
        self.day_cycle = DayCycleSystem(self.time_system)
        self.event_system = EventSystem(self.farm, self.player)
        self.event_system.game = self  # Allow event system to access game state
        self.market_inflated = False
        self.lazy_day_active = False
        self.fishing_bonus = False
        self.last_update_time = datetime.now()
    
    def update(self) -> List[str]:
        """Update all game systems and return any messages from the update."""
        messages = []
        
        # Update day cycle
        day_cycle_msg = self.day_cycle.update()
        if day_cycle_msg:
            messages.append(day_cycle_msg)
        
        # Check if day has changed
        if self.day_cycle.get_current_part() == "night":
            self.time_system.update()
            messages.append(f"Day {self.time_system.day} has begun!")
            
            # Update weather
            self.weather_system.update()
            messages.append(f"The weather is {self.weather_system.get_weather()} today.")
            
            # Check for events
            event_msg = self.event_system.update(self.time_system.day)
            if event_msg:
                messages.append(event_msg)
            
            # Reset daily modifiers
            self.market_inflated = False
            self.lazy_day_active = False
            self.fishing_bonus = False
        
        # Update last update time
        self.last_update_time = datetime.now()
        
        return messages
    
    def plant_crop(self, plot_index: int, crop_name: str) -> str:
        """Plant a crop in the specified plot."""
        crop = self.crop_system.get_crop(crop_name)
        if not crop:
            return f"Unknown crop: {crop_name}"
        
        if crop_name not in self.crop_system.unlocked_crops:
            return f"You haven't unlocked {crop_name} yet!"
        
        if self.market_inflated:
            cost = crop.cost * 2
        else:
            cost = crop.cost
        
        if not self.player.can_afford(cost):
            return f"Not enough money! You need ${cost} to plant {crop_name}."
        
        if not self.player.has_stamina(crop.stamina_cost):
            return f"Not enough stamina! You need {crop.stamina_cost} hearts to plant {crop_name}."
        
        self.player.spend_money(cost)
        self.player.use_stamina(crop.stamina_cost)
        self.farm.plant_crop(plot_index, crop)
        return f"Planted {crop_name} in plot {plot_index + 1}!"
    
    def harvest_crops(self) -> str:
        """Harvest all ready crops and return a message."""
        total = self.farm.harvest_ready_crops()
        if total > 0:
            if self.market_inflated:
                total *= 2
            self.player.earn_money(total)
            return f"Harvested crops worth ${total}!"
        return "No crops ready for harvest."
    
    def sleep(self) -> str:
        """Make the player sleep to restore stamina."""
        if self.player.stamina >= self.player.max_stamina:
            return "You're not tired!"
        
        self.player.full_restore()
        return "You had a good night's sleep! Stamina fully restored."
    
    def save(self) -> str:
        """Save the game state to a file."""
        try:
            with open(self.SAVE_FILE, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return "Game saved successfully!"
        except Exception as e:
            return f"Failed to save game: {str(e)}"
    
    @classmethod
    def load(cls) -> 'Game':
        """Load the game state from a file."""
        try:
            if not os.path.exists(cls.SAVE_FILE):
                return cls()
            
            with open(cls.SAVE_FILE, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Failed to load game: {str(e)}")
            return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'player': self.player.to_dict(),
            'farm': self.farm.to_dict(),
            'crop_system': self.crop_system.to_dict(),
            'weather_system': self.weather_system.to_dict(),
            'time_system': self.time_system.to_dict(),
            'day_cycle': self.day_cycle.to_dict(),
            'market_inflated': self.market_inflated,
            'lazy_day_active': self.lazy_day_active,
            'fishing_bonus': self.fishing_bonus,
            'last_update_time': self.last_update_time.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Game':
        game = cls()
        game.player = Player.from_dict(data['player'])
        game.farm = FarmSystem.from_dict(data['farm'])
        game.crop_system = CropSystem.from_dict(data['crop_system'])
        game.weather_system = WeatherSystem.from_dict(data['weather_system'])
        game.time_system = TimeSystem.from_dict(data['time_system'])
        game.day_cycle = DayCycleSystem.from_dict(data['day_cycle'])
        game.event_system = EventSystem(game.farm, game.player)
        game.event_system.game = game
        game.market_inflated = data.get('market_inflated', False)
        game.lazy_day_active = data.get('lazy_day_active', False)
        game.fishing_bonus = data.get('fishing_bonus', False)
        game.last_update_time = datetime.fromisoformat(data['last_update_time'])
        return game 