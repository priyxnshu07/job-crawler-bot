@echo off
title Job Crawler Bot - Starting...
color 0A
echo.
echo ========================================
echo    JOB CRAWLER BOT - STARTING
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run SETUP.bat first!
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Note: Email configuration is now done through web UI
REM No need for .env file - users configure email in the app!

echo.
echo Starting services...
echo.

REM Start Flask in new window
echo [1/3] Starting Flask app...
start "Job Crawler - Flask" cmd /k "venv\Scripts\python.exe app.py"
timeout /t 4 /nobreak >nul

REM Start Celery Worker in new window
echo [2/3] Starting Celery worker...
start "Job Crawler - Worker" cmd /k "venv\Scripts\python.exe -m celery -A tasks worker --loglevel INFO"
timeout /t 3 /nobreak >nul

REM Start Celery Beat in new window
echo [3/3] Starting Celery scheduler...
start "Job Crawler - Scheduler" cmd /k "venv\Scripts\python.exe -m celery -A tasks beat --loglevel INFO"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    APPLICATION IS RUNNING!
echo ========================================
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://127.0.0.1:5001
echo.
echo ========================================
echo    HOW TO USE:
echo ========================================
echo.
echo 1. Browser should open automatically
echo 2. If not, visit: http://127.0.0.1:5001
echo 3. Register/Login to use the app
echo.
echo TO STOP:
echo - Close all 3 windows (Flask, Worker, Scheduler)
echo - OR close this window
echo.
echo ========================================
pause

