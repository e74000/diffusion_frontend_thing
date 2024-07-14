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

# Step 3: Check and fetch safe.h5 if not exists
SAFE_H5="safe.h5"

if [ ! -f "$SAFE_H5" ]; then
  echo "Fetching safe.h5..."
  curl -o $SAFE_H5 https://r2.e74000.net/diffusion_frontend_thing/safe.h5
else
  echo "safe.h5 already exists."
fi

echo "Initialization complete."
