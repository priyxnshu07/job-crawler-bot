@echo off
REM Job Crawler Bot - Windows Launcher
REM Double-click this file to start the application

echo ========================================
echo   Job Crawler Bot - Starting...
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   setup.bat
    echo.
    pause
    exit /b 1
)

REM Load .env if exists
if exist ".env" (
    echo Loading .env file...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set "%%a=%%b"
    )
)

echo Starting services...
echo.

REM Start Flask
echo [1/3] Starting Flask app...
start "Flask App" cmd /k "venv\Scripts\python.exe app.py"
timeout /t 3 /nobreak >nul

REM Start Celery Worker
echo [2/3] Starting Celery worker...
start "Celery Worker" cmd /k "venv\Scripts\python.exe -m celery -A tasks worker --loglevel INFO"
timeout /t 2 /nobreak >nul

REM Start Celery Beat
echo [3/3] Starting Celery scheduler...
start "Celery Beat" cmd /k "venv\Scripts\python.exe -m celery -A tasks beat --loglevel INFO"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   Application is running!
echo ========================================
echo.
echo Opening browser...
start http://127.0.0.1:5001
echo.
echo Press any key to close this window (services will keep running)
echo To stop, close the Flask, Celery Worker, and Celery Beat windows
pause


