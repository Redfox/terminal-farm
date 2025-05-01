let selectedPlot = null;
let selectedCrop = null;

async function fetchGameState() {
    try {
        const response = await fetch('/api/game/state');
        const data = await response.json();
        
        // Update status bar
        document.getElementById('day').textContent = data.day;
        document.getElementById('time').textContent = data.time;
        document.getElementById('weather').textContent = data.weather;
        document.getElementById('money').textContent = `$${data.money}`;
        document.getElementById('stamina').textContent = '❤'.repeat(Math.floor(data.stamina));
        
        // Update plots
        const plotsContainer = document.querySelector('.plots-container');
        plotsContainer.innerHTML = data.plots.map((plot, index) => `
            <div class="plot" onclick="selectPlot(${index})">
                <div class="plot-content" ${!plot.crop ? 'class="empty"' : ''}>
                    ${plot.crop ? `
                        <div class="crop-name">${plot.crop}</div>
                        <div class="growth-bar">
                            <div class="growth-progress" style="width: ${plot.growth_progress * 100}%"></div>
                        </div>
                    ` : `
                        <div class="empty-plot">Empty</div>
                    `}
                </div>
                <div class="plot-number">${index + 1}</div>
            </div>
        `).join('');
        
        // Update available crops
        const cropsList = document.querySelector('.crops-list');
        cropsList.innerHTML = `
            <h3>Available Crops</h3>
            ${data.available_crops.map(crop => `
                <div class="crop-item" onclick="selectCrop('${crop.name}')">
                    <div class="crop-name">${crop.name}</div>
                    <div class="crop-details">
                        <span>Cost: $${crop.cost}</span>
                        <span>Value: $${crop.value}</span>
                        <span>Growth: ${crop.growth_time}s</span>
                    </div>
                </div>
            `).join('')}
        `;
    } catch (error) {
        console.error('Error fetching game state:', error);
        addMessage('Error updating game state');
    }
}

function selectPlot(index) {
    selectedPlot = index;
    if (selectedCrop) {
        plantCrop();
    }
}

function selectCrop(name) {
    selectedCrop = name;
    if (selectedPlot !== null) {
        plantCrop();
    }
}

async function plantCrop() {
    if (selectedPlot === null || selectedCrop === null) {
        addMessage('Please select both a plot and a crop!');
        return;
    }
    
    try {
        const response = await fetch('/api/game/plant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                plot_index: selectedPlot,
                crop_name: selectedCrop
            })
        });
        
        const data = await response.json();
        addMessage(data.message);
        selectedPlot = null;
        selectedCrop = null;
        fetchGameState();
    } catch (error) {
        console.error('Error planting crop:', error);
        addMessage('Failed to plant crop!');
    }
}

async function harvestCrops() {
    try {
        const response = await fetch('/api/game/harvest', {
            method: 'POST'
        });
        
        const data = await response.json();
        addMessage(data.message);
        fetchGameState();
    } catch (error) {
        console.error('Error harvesting crops:', error);
        addMessage('Failed to harvest crops!');
    }
}

async function sleep() {
    try {
        const response = await fetch('/api/game/sleep', {
            method: 'POST'
        });
        
        const data = await response.json();
        addMessage(data.message);
        fetchGameState();
    } catch (error) {
        console.error('Error sleeping:', error);
        addMessage('Failed to sleep!');
    }
}

async function saveGame() {
    try {
        const response = await fetch('/api/game/save', {
            method: 'POST'
        });
        
        const data = await response.json();
        addMessage(data.message);
    } catch (error) {
        console.error('Error saving game:', error);
        addMessage('Failed to save game!');
    }
}

function addMessage(message) {
    const messagesDiv = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    messageElement.textContent = message;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Initial fetch and periodic updates
fetchGameState();
setInterval(fetchGameState, 5000); 