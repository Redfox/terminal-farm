import unittest
from terminal_farm.core.game import GameState

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.game = GameState()

    def test_initial_state(self):
        self.assertEqual(self.game.player.money, 100)
        self.assertEqual(self.game.player.stamina, 100)
        self.assertEqual(self.game.time_system.current_day, 1)
        self.assertEqual(len(self.game.farm_system.plots), 9)

    def test_plant_crop(self):
        # Test planting a crop
        self.game.plant_crop(0, "Wheat")
        self.assertEqual(self.game.farm_system.plots[0].crop.name, "Wheat")
        self.assertEqual(self.game.player.stamina, 90)  # Stamina should decrease

    def test_harvest_crop(self):
        # Plant a crop
        self.game.plant_crop(0, "Wheat")
        # Fast forward growth
        self.game.crop_system.grow_crops()
        # Harvest the crop
        self.game.harvest_ready_crops()
        self.assertIsNone(self.game.farm_system.plots[0].crop)
        self.assertGreater(self.game.player.money, 100)  # Money should increase

    def test_sleep(self):
        initial_day = self.game.time_system.current_day
        self.game.sleep()
        self.assertEqual(self.game.time_system.current_day, initial_day + 1)
        self.assertEqual(self.game.player.stamina, 100)  # Stamina should be restored

    def test_save_load(self):
        # Modify game state
        self.game.plant_crop(0, "Wheat")
        self.game.player.money = 200
        # Save game
        self.game.save()
        # Create new game state
        new_game = GameState()
        # Load saved game
        new_game.load()
        self.assertEqual(new_game.farm_system.plots[0].crop.name, "Wheat")
        self.assertEqual(new_game.player.money, 200)

if __name__ == '__main__':
    unittest.main() 