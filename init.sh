#!/bin/bash

set -e

# Step 1: Build frontend
echo "Building frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

npm run build
cd ..

# Step 2: Fetch backend dependencies
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

echo "Installing backend dependencies..."
pip install -r requirements.txt

# Step 3: Check and fetch safe.csv if not exists
SAFE_CSV="safe.csv"

if [ ! -f "$SAFE_CSV" ]; then
  echo "Fetching safe.csv..."
  curl -o $SAFE_CSV https://r2.e74000.net/diffusion_frontend_thing/safe.csv
else
  echo "safe.csv already exists."
fi

echo "Initialization complete."
