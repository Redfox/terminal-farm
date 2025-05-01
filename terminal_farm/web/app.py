from flask import Flask, render_template, jsonify, request
from ..core.game import Game
import json

app = Flask(__name__)
game = Game.load()

@app.route('/')
def index():
    # Get the current game state
    plots = [
        {
            'crop': plot.crop.name if plot.crop else None,
            'growth_progress': plot.growth_progress
        }
        for plot in game.farm.plots
    ]
    
    available_crops = [
        {
            'name': crop.name,
            'cost': crop.cost * 2 if game.market_inflated else crop.cost,
            'growth_time': crop.growth_time,
            'value': crop.value,
            'stamina_cost': crop.stamina_cost
        }
        for crop in game.crop_system.get_unlocked_crops()
    ]
    
    return render_template('index.html',
        day=game.time_system.day,
        time=game.day_cycle.get_current_part(),
        weather=game.weather_system.get_weather(),
        money=game.player.money,
        stamina=game.player.stamina,
        max_stamina=game.player.max_stamina,
        plots=plots,
        available_crops=available_crops
    )

@app.route('/api/game/state')
def get_game_state():
    return jsonify({
        'day': game.time_system.day,
        'time': game.day_cycle.get_current_part(),
        'weather': game.weather_system.get_weather(),
        'money': game.player.money,
        'stamina': game.player.stamina,
        'max_stamina': game.player.max_stamina,
        'plots': [
            {
                'crop': plot.crop.name if plot.crop else None,
                'growth_progress': plot.growth_progress
            }
            for plot in game.farm.plots
        ],
        'available_crops': [
            {
                'name': crop.name,
                'cost': crop.cost * 2 if game.market_inflated else crop.cost,
                'growth_time': crop.growth_time,
                'value': crop.value,
                'stamina_cost': crop.stamina_cost
            }
            for crop in game.crop_system.get_unlocked_crops()
        ]
    })

@app.route('/api/game/plant', methods=['POST'])
def plant_crop():
    data = request.json
    plot_index = data.get('plot_index')
    crop_name = data.get('crop_name')
    
    if plot_index is None or crop_name is None:
        return jsonify({'error': 'Missing plot_index or crop_name'}), 400
    
    message = game.plant_crop(plot_index, crop_name)
    game.update()
    return jsonify({'message': message})

@app.route('/api/game/harvest', methods=['POST'])
def harvest_crops():
    message = game.harvest_crops()
    game.update()
    return jsonify({'message': message})

@app.route('/api/game/sleep', methods=['POST'])
def sleep():
    message = game.sleep()
    game.update()
    return jsonify({'message': message})

@app.route('/api/game/save', methods=['POST'])
def save_game():
    message = game.save()
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True) 