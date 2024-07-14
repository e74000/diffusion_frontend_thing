@echo off
setlocal

:: Step 1: Build frontend
echo Building frontend...
cd frontend

if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
)

npm run build
cd ..

:: Step 2: Fetch backend dependencies
echo Setting up backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing backend dependencies...
pip install -r requirements.txt

:: Step 3: Check and fetch safe.csv if not exists
set SAFE_CSV=backend\safe.csv

if not exist "%SAFE_CSV%" (
    echo Fetching safe.csv...
    curl -o "%SAFE_CSV%" https://r2.e74000.net/diffusion_frontend_thing/safe.csv
) else (
    echo safe.csv already exists.
)

echo Initialization complete.
endlocal
