@echo off
REM AiD Bot Startup Script
REM Activates virtual environment and starts the bot

echo ========================================
echo Starting AiD Discord Bot
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo [STARTUP] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if bot.py exists
if not exist "bot.py" (
    echo [ERROR] bot.py not found in current directory!
    pause
    exit /b 1
)

echo [STARTUP] Starting bot...
echo.
python bot.py

REM If bot exits, pause to see error messages
if errorlevel 1 (
    echo.
    echo [ERROR] Bot exited with error code: %errorlevel%
    pause
)
