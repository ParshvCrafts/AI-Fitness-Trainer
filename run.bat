@echo off
REM AI Fitness Trainer Startup Script for Windows

echo =====================================
echo   AI Fitness Trainer Starting...
echo =====================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Create logs directory if it doesn't exist
if not exist "logs\" mkdir logs

REM Start the application
echo Starting AI Fitness Trainer on http://localhost:5000
echo Press Ctrl+C to stop the server
echo =====================================

python app.py

pause
