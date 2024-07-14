#!/bin/bash

set -e

# Activate the virtual environment
echo "Activating virtual environment..."
cd backend
source venv/bin/activate

# Run main.py with arguments
echo "Running backend main.py..."
python main.py "$@"
