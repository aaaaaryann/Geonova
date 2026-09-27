@echo off
setlocal enabledelayedexpansion
title Geonova Server

echo =========================================================
echo Starting Geonova: Smart Tourist Safety ^& Tourism Platform
echo =========================================================
echo.

:: Switch to the backend directory relative to this script
cd /d "%~dp0backend"

:: Verify Python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not found in your PATH.
        echo Please install Python 3.10+ from https://www.python.org/ or check your PATH environment variable.
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo Initializing server on http://127.0.0.1:8000 ...
echo Opening http://127.0.0.1:8000 in your web browser...
echo Press CTRL+C to stop the server.
echo.

:: Launch browser automatically in background after a brief delay for server initialization
start "" cmd /c "ping -n 3 127.0.0.1 >nul & start http://127.0.0.1:8000"

%PYTHON_CMD% -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server terminated with an error code: %errorlevel%
    echo If required packages are missing, run: pip install -r requirements.txt (or install fastapi uvicorn)
    echo.
)

pause

