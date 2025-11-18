@echo off
REM Quick fix for NLTK_IMPORT_ERROR
REM This fixes the transformers/sentence-transformers version conflict

echo ========================================
echo AiD Quick Fix - Version Conflict
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo [FIX] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [FIX] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [FIX] Fixing transformers and sentence-transformers versions...
pip uninstall -y transformers sentence-transformers

echo.
echo [FIX] Installing compatible versions...
pip install transformers>=4.35.0 sentence-transformers>=2.3.0

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed
    echo Try running as Administrator
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Version conflict fixed!
echo ========================================
echo.
echo The NLTK_IMPORT_ERROR should now be resolved.
echo.
echo You can now start the bot:
echo - Run: start_bot.bat
echo   OR
echo - Run: python bot.py
echo.
pause
