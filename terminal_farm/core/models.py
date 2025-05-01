import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod

class ISerializable(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        pass

class IGameSystem(ABC):
    @abstractmethod
    def update(self):
        pass

class Crop(ISerializable):
    def __init__(self, name: str, cost: int, growth_time: int, value: int, 
                 color: str, stamina_cost: float):
        self.name = name
        self.cost = cost
        self.growth_time = growth_time
        self.value = value
        self.color = color
        self.stamina_cost = stamina_cost
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'cost': self.cost,
            'growth_time': self.growth_time,
            'value': self.value,
            'color': self.color,
            'stamina_cost': self.stamina_cost
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Crop':
        return cls(
            name=data['name'],
            cost=data['cost'],
            growth_time=data['growth_time'],
            value=data['value'],
            color=data['color'],
            stamina_cost=data['stamina_cost']
        )

class Plot(ISerializable):
    def __init__(self, crop: Optional[Crop] = None, planted_at: Optional[datetime] = None):
        self.crop = crop
        self.planted_at = planted_at
    
    @property
    def is_empty(self) -> bool:
        return self.crop is None
    
    @property
    def growth_progress(self) -> float:
        if self.is_empty or self.planted_at is None:
            return 0.0
        
        elapsed = (datetime.now() - self.planted_at).total_seconds()
        return min(1.0, elapsed / self.crop.growth_time)
    
    @property
    def is_ready(self) -> bool:
        return self.growth_progress >= 1.0
    
    def plant(self, crop: Crop):
        self.crop = crop
        self.planted_at = datetime.now()
    
    def harvest(self) -> int:
        if self.is_empty or not self.is_ready:
            return 0
        
        value = self.crop.value
        self.crop = None
        self.planted_at = None
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'crop': self.crop.to_dict() if self.crop else None,
            'planted_at': self.planted_at.isoformat() if self.planted_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plot':
        crop_data = data['crop']
        planted_at = data['planted_at']
        
        return cls(
            crop=Crop.from_dict(crop_data) if crop_data else None,
            planted_at=datetime.fromisoformat(planted_at) if planted_at else None
        )

class Player(ISerializable):
    def __init__(self, money: int = 50, stamina: float = 5.0, 
                 max_stamina: int = 5, last_sleep_time: Optional[datetime] = None):
        self.money = money
        self.stamina = stamina
        self.max_stamina = max_stamina
        self.last_sleep_time = last_sleep_time or datetime.now()
        self.has_farmdex = False
        self.fossils_found = []
    
    def can_afford(self, amount: int) -> bool:
        return self.money >= amount
    
    def spend_money(self, amount: int):
        self.money -= amount
    
    def earn_money(self, amount: int):
        self.money += amount
    
    def has_stamina(self, amount: float) -> bool:
        return self.stamina >= amount
    
    def use_stamina(self, amount: float):
        self.stamina -= amount
    
    def restore_stamina(self, amount: float):
        self.stamina = min(self.max_stamina, self.stamina + amount)
    
    def full_restore(self):
        self.stamina = self.max_stamina
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'money': self.money,
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'last_sleep_time': self.last_sleep_time.isoformat(),
            'has_farmdex': getattr(self, 'has_farmdex', False),
            'fossils_found': getattr(self, 'fossils_found', [])
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        obj = cls(
            money=data['money'],
            stamina=data['stamina'],
            max_stamina=data['max_stamina'],
            last_sleep_time=datetime.fromisoformat(data['last_sleep_time'])
        )
        obj.has_farmdex = data.get('has_farmdex', False)
        obj.fossils_found = data.get('fossils_found', [])
        return obj

class FarmSystem(ISerializable):
    def __init__(self, size: int = 9):
        self.plots = [Plot() for _ in range(size)]
    
    def plant_crop(self, plot_index: int, crop: Crop):
        if 0 <= plot_index < len(self.plots):
            self.plots[plot_index].plant(crop)
    
    def harvest_ready_crops(self) -> int:
        total = 0
        for plot in self.plots:
            if not plot.is_empty and plot.is_ready:
                total += plot.harvest()
        return total
    
    def get_plot_status(self, plot_index: int) -> Tuple[Optional[Crop], float]:
        if 0 <= plot_index < len(self.plots):
            plot = self.plots[plot_index]
            return plot.crop, plot.growth_progress
        return None, 0.0
    
    def damage_random_crop(self) -> str:
        empty_plots = [i for i, plot in enumerate(self.plots) if not plot.is_empty]
        if not empty_plots:
            return None
        
        plot_index = random.choice(empty_plots)
        plot = self.plots[plot_index]
        crop_name = plot.crop.name
        plot.crop = None
        plot.planted_at = None
        return f"A storm destroyed your {crop_name}!"
    
    def apply_growth_bonus(self, bonus_percent: int) -> str:
        for plot in self.plots:
            if not plot.is_empty and plot.planted_at is not None:
                elapsed = (datetime.now() - plot.planted_at).total_seconds()
                bonus_time = elapsed * (bonus_percent / 100)
                plot.planted_at = datetime.now() - timedelta(seconds=elapsed + bonus_time)
        return f"Your crops grew {bonus_percent}% faster today!"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'plots': [plot.to_dict() for plot in self.plots]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FarmSystem':
        farm = cls(size=len(data['plots']))
        farm.plots = [Plot.from_dict(plot_data) for plot_data in data['plots']]
        return farm

class CropSystem(ISerializable):
    def __init__(self):
        self.available_crops = self._load_default_crops()
        self.unlocked_crops = ['wheat']
    
    def _load_default_crops(self) -> Dict[str, Crop]:
        return {
            'wheat': Crop('wheat', 10, 10, 20, 'yellow', 0.5),
            'corn': Crop('corn', 20, 20, 45, 'bright_yellow', 0.5),
            'pumpkin': Crop('pumpkin', 40, 40, 100, 'orange', 1.0),
            'carrot': Crop('carrot', 15, 12, 25, 'orange', 0.5),
            'eggplant': Crop('eggplant', 35, 30, 70, 'purple', 1.0),
            'blueberry': Crop('blueberry', 60, 35, 90, 'blue', 1.0),
            'lazy_ghost': Crop('lazy ghost seed [rare]', 0, 30, 100, 'white', 0),
        }
    
    def get_crop(self, name: str) -> Optional[Crop]:
        return self.available_crops.get(name)
    
    def unlock_crop(self, name: str):
        if name in self.available_crops and name not in self.unlocked_crops:
            self.unlocked_crops.append(name)
            return f"NEW CROP UNLOCKED: {name.capitalize()}!"
        return None
    
    def get_unlocked_crops(self) -> List[Crop]:
        return [self.available_crops[name] for name in self.unlocked_crops]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'unlocked_crops': self.unlocked_crops
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CropSystem':
        system = cls()
        system.unlocked_crops = data['unlocked_crops']
        return system

class WeatherSystem(IGameSystem):
    WEATHER_TYPES = ['sunny', 'rainy', 'cloudy', 'windy']
    
    def __init__(self):
        self.current_weather = 'sunny'
    
    def update(self):
        if random.random() < 0.2:
            self.current_weather = random.choice(self.WEATHER_TYPES)
    
    def get_weather(self) -> str:
        return self.current_weather
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'current_weather': self.current_weather
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherSystem':
        system = cls()
        system.current_weather = data['current_weather']
        return system

class TimeSystem(IGameSystem):
    def __init__(self):
        self.day = 1
    
    def update(self):
        self.day += 1
    
    def get_day(self) -> int:
        return self.day
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'day': self.day
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeSystem':
        system = cls()
        system.day = data['day']
        return system

class EventSystem(IGameSystem):
    def __init__(self, farm: FarmSystem, player: Player):
        self.farm = farm
        self.player = player
        self.last_event_day = -1
    
    def update(self, current_day: int):
        base_chance = 0.4
        if random.random() < base_chance and self.last_event_day != current_day:
            self.last_event_day = current_day
            event = random.choice([
                self._storm_event,
                self._sunny_bonus_event,
                self._found_money_event,
                self._found_energy_event,
                self._fish_rain_event,
                self._plague_event,
                self._spirit_farmer_event,
                self._lazy_day_event,
                self._starry_night_event,
                self._inflated_market_event,
                self._night_robbery_event,
                self._perfect_fishing_day_event,
                self._rich_farmer_patron_event,
                self._sugar_daddy_marriage_event
            ])
            return event()
        return None

    def _rich_farmer_patron_event(self):
        amount = 500
        self.player.earn_money(amount)
        return "Your charm paid off. A rich old farmer who just loves your crops appears. 💖 (+$500)"

    def _sugar_daddy_marriage_event(self):
        amount = 3000
        self.player.earn_money(amount)
        return "Farm life is tough… unless you marry rich! 💍 (+$3,000)"
    
    def _storm_event(self):
        return self.farm.damage_random_crop()
    
    def _sunny_bonus_event(self):
        return self.farm.apply_growth_bonus(20)
    
    def _found_money_event(self):
        amount = random.randint(10, 50)
        self.player.earn_money(amount)
        return f"You found money on the ground! (+${amount})"
    
    def _found_energy_event(self):
        self.player.restore_stamina(1)
        return "You found an energy drink! (+1 heart)"

    def _fish_rain_event(self):
        if hasattr(self, "game") and hasattr(self.game, "fishing_system"):
            self.game.fishing_system.caught_fish.append({"name": "Skyfish", "value": 150})
            return "A mysterious rain dropped a Skyfish into your bucket! (+$150)"
        return None

    def _plague_event(self):
        damaged = 0
        for _ in range(2):
            result = self.farm.damage_random_crop()
            if result:
                damaged += 1
        if damaged:
            return "A mysterious plague destroyed some crops!"
        return None

    def _spirit_farmer_event(self):
        if hasattr(self, "game") and hasattr(self.game, "crop_system"):
            if "lazy_ghost" not in self.game.crop_system.unlocked_crops:
                self.game.crop_system.unlocked_crops.append("lazy_ghost")
        return "A benevolent spirit gifted you a Lazy Ghost Seed!"

    def _lazy_day_event(self):
        if self.player.max_stamina > 1:
            self.player.max_stamina -= 2
            if self.player.stamina > self.player.max_stamina:
                self.player.stamina = self.player.max_stamina
            if hasattr(self, "game"):
                self.game.lazy_day_active = True
            return "You feel extremely lazy today... (-2 Max Hearts)"
        return None

    def _starry_night_event(self):
        return self.farm.apply_growth_bonus(100)

    def _inflated_market_event(self):
        if hasattr(self, "game"):
            self.game.market_inflated = True
        return "Prices have doubled today! (Inflated Market)"

    def _night_robbery_event(self):
        stolen = min(100, self.player.money)
        self.player.spend_money(stolen)
        return f"Thieves stole ${stolen} from your farm during the night!"

    def _perfect_fishing_day_event(self):
        if hasattr(self, "game"):
            self.game.fishing_bonus = True
        return "The fish are biting! (+50% fish value today!)"

class DayCycleSystem(ISerializable):
    PARTS = ["morning", "afternoon", "evening", "night"]

    def __init__(self, time_system: TimeSystem):
        self.time_system = time_system
        self.current_part_index = 0
        self.last_update_time = datetime.now()
        self.durations = self.get_durations_for_current_season()

    def get_season(self) -> str:
        season_index = (self.time_system.day - 1) // 30 % 4
        return ["spring", "summer", "autumn", "winter"][season_index]

    def get_durations_for_current_season(self) -> Dict[str, int]:
        season = self.get_season()
        
        if season == "summer":
            return {"morning": 4, "afternoon": 4, "evening": 2, "night": 3}
        elif season == "winter":
            return {"morning": 3, "afternoon": 3, "evening": 4, "night": 3}
        else:
            return {"morning": 3, "afternoon": 3, "evening": 3, "night": 3}

    def update(self):
        now = datetime.now()
        current_part = self.PARTS[self.current_part_index]
        duration_minutes = self.durations[current_part]

        if (now - self.last_update_time).total_seconds() >= duration_minutes * 60:
            self.current_part_index = (self.current_part_index + 1) % len(self.PARTS)
            self.last_update_time = now
            self.durations = self.get_durations_for_current_season()
            return f"Part of the day changed: {self.get_current_part().capitalize()}!"
        return None

    def get_current_part(self) -> str:
        return self.PARTS[self.current_part_index]

    def to_dict(self):
        return {
            'current_part_index': self.current_part_index,
            'last_update_time': self.last_update_time.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        instance = cls(TimeSystem())
        instance.current_part_index = data['current_part_index']
        instance.last_update_time = datetime.fromisoformat(data['last_update_time'])
        return instance 