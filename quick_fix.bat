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
echo [FIX] Fixing package version conflicts...
pip uninstall -y transformers sentence-transformers pandas numpy

echo.
echo [FIX] Installing compatible versions...
echo - transformers + sentence-transformers (fixes NLTK_IMPORT_ERROR)
echo - pandas + numpy (compatible with TTS 0.22.0)
pip install "transformers>=4.35.0,<5.0.0" "sentence-transformers>=2.3.0"
pip install "pandas>=1.4,<2.0" "numpy>=1.24.0,<2.0"

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
