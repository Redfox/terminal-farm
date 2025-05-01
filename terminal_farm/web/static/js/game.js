class Game {
    constructor() {
        this.state = null;
        this.selectedPlot = null;
        this.initializeEventListeners();
        this.loadGameState();
    }

    async loadGameState() {
        try {
            const response = await fetch('/api/game/state');
            this.state = await response.json();
            this.updateUI();
        } catch (error) {
            console.error('Error loading game state:', error);
        }
    }

    async performAction(action, params = {}) {
        try {
            const response = await fetch('/api/game/action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action, params }),
            });
            const result = await response.json();
            if (result.error) {
                alert(result.error);
            } else {
                await this.loadGameState();
            }
        } catch (error) {
            console.error('Error performing action:', error);
        }
    }

    updateUI() {
        // Update status bar
        document.getElementById('day').textContent = `Day: ${this.state.time_system.day}`;
        document.getElementById('money').textContent = `💰 Money: $${this.state.player.money}`;
        document.getElementById('stamina').textContent = `❤️ Stamina: ${this.state.player.stamina}/${this.state.player.max_stamina}`;
        document.getElementById('weather').textContent = `☀️ Weather: ${this.state.weather_system.current_weather}`;

        // Update farm grid
        this.state.farm.plots.forEach((plot, index) => {
            const plotElement = document.querySelector(`[data-plot="${index}"] .plot-content`);
            if (plot.crop) {
                const progress = Math.min(100, Math.floor(plot.growth_progress * 100));
                plotElement.textContent = `${plot.crop.name} (${progress}%)`;
                plotElement.style.color = plot.crop.color;
            } else {
                plotElement.textContent = 'Empty';
                plotElement.style.color = 'inherit';
            }
        });
    }

    initializeEventListeners() {
        // Plot selection
        document.querySelectorAll('.plot').forEach(plot => {
            plot.addEventListener('click', () => {
                if (document.querySelector('.crop-selection').style.display === 'block') {
                    this.selectedPlot = plot.dataset.plot;
                    this.showCropSelection();
                }
            });
        });

        // Action buttons
        document.getElementById('plant-btn').addEventListener('click', () => {
            this.showCropSelection();
        });

        document.getElementById('harvest-btn').addEventListener('click', () => {
            this.performAction('harvest');
        });

        document.getElementById('next-day-btn').addEventListener('click', () => {
            this.performAction('next_day');
        });

        document.getElementById('sleep-btn').addEventListener('click', () => {
            this.performAction('sleep');
        });

        document.getElementById('merchant-btn').addEventListener('click', () => {
            // TODO: Implement merchant interface
            alert('Merchant interface coming soon!');
        });

        document.getElementById('fishing-btn').addEventListener('click', () => {
            this.performAction('fish');
        });
    }

    showCropSelection() {
        const cropSelection = document.querySelector('.crop-selection');
        const cropList = document.getElementById('crop-list');
        
        cropList.innerHTML = '';
        this.state.crop_system.unlocked_crops.forEach(crop => {
            const cropItem = document.createElement('div');
            cropItem.className = 'crop-item';
            cropItem.textContent = `${crop.name} ($${crop.cost})`;
            cropItem.addEventListener('click', () => {
                this.performAction('plant', {
                    plot_index: this.selectedPlot,
                    crop_name: crop.name
                });
                cropSelection.style.display = 'none';
            });
            cropList.appendChild(cropItem);
        });

        cropSelection.style.display = 'block';
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new Game();
}); 