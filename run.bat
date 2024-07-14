@echo off
setlocal

:: Activate the virtual environment
echo Activating virtual environment...
cd backend
call venv\Scripts\activate

:: Run main.py with arguments
echo Running backend main.py...
python main.py %*

endlocal
