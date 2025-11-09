#!/bin/bash

# AI Fitness Trainer Startup Script

echo "====================================="
echo "  AI Fitness Trainer Starting...   "
echo "====================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=${FLASK_ENV:-development}

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the application
echo "Starting AI Fitness Trainer on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "====================================="

python app.py
