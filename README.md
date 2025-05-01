# Terminal Farm

A farming game that can be played in both terminal and web interfaces. Grow crops, manage your farm, and earn money!

## Features

- Plant and harvest various crops
- Dynamic weather system
- Day/night cycle
- Random events
- Save/load game state
- Both terminal and web interfaces
- Responsive design for web interface

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/terminal-farm.git
cd terminal-farm
```

2. Install the package:

```bash
pip install -e .
```

## Usage

### Terminal Interface

To play the game in the terminal:

```bash
terminal-farm
```

### Web Interface

To play the game in your web browser:

```bash
python -m terminal_farm.web.app
```

Then open your browser and navigate to `http://localhost:5000`

## Game Controls

### Terminal Interface

- Use numbers 1-5 to select actions from the menu
- Follow prompts to plant crops and manage your farm

### Web Interface

- Click on plots to select them
- Click on crops to plant them
- Use buttons to harvest, sleep, and save

## Game Mechanics

- Each crop has different growth times and values
- Crops require stamina to plant
- Weather affects crop growth
- Random events can occur during gameplay
- Save your progress to continue later

## Development

To contribute to the project:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
