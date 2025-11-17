@echo off
REM Job Crawler Bot - Windows Setup Script

echo ========================================
echo   Job Crawler Bot - Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Downloading spaCy model...
python -m spacy download en_core_web_sm

echo Setting up database...
python database_setup.py

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Double-click RUN.bat to start the application
echo 2. Browser will open automatically
echo 3. Register/Login to use the app
echo.
echo NOTE: Email configuration can be done through
echo       the web interface - no .env file needed!
echo.
echo ========================================
pause


