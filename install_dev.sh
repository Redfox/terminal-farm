#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install package in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8

echo "Installation complete! You can now run:"
echo "- ./run_dev.py --mode terminal  # For terminal mode"
echo "- ./run_dev.py --mode web       # For web mode"
echo "- ./run_tests.py                # To run tests" 