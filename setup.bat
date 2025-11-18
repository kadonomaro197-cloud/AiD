@echo off
REM AiD Setup Script for Windows
REM This script sets up your virtual environment and installs all dependencies

echo ========================================
echo AiD Discord Bot - Initial Setup
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found
) else (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo Make sure Python is installed and in PATH
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [SETUP] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [SETUP] Installing dependencies from requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Some packages failed to install
    echo.
    echo Common issues:
    echo - PyAudio: May need Microsoft C++ Build Tools
    echo   Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    echo - FFmpeg: Download from https://ffmpeg.org/download.html
    echo   Extract and add to PATH
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Setup complete!
echo ========================================
echo.
echo To start AiD:
echo 1. Run: start_bot.bat
echo    OR
echo 2. Activate venv: venv\Scripts\activate.bat
echo    Then run: python bot.py
echo.
pause
