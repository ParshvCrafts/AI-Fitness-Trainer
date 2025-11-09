@echo off
REM Setup HTTPS for AI Fitness Trainer - Windows

echo =====================================
echo   AI Fitness Trainer - HTTPS Setup
echo =====================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install pyOpenSSL
echo Installing pyOpenSSL...
pip install pyOpenSSL

REM Generate certificate
echo.
echo Generating SSL certificate...
python generate_cert.py

echo.
echo =====================================
echo   Setup Complete!
echo =====================================
echo.
echo Next step: Run the HTTPS server
echo   python app_https.py
echo.
echo Then open: https://10.42.108.58:5000
echo.
echo =====================================

pause
