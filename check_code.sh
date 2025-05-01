#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run flake8
echo "Running flake8..."
flake8 terminal_farm tests

# Run black
echo "Running black..."
black terminal_farm tests

# Run tests with coverage
echo "Running tests with coverage..."
pytest --cov=terminal_farm tests/

echo "Code quality checks complete!" 