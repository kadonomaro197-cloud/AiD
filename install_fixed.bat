@echo off
REM One-command fix for all dependency issues
REM This installs everything with correct version constraints

echo ========================================
echo AiD Complete Installation Fix
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
)

echo [INSTALL] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [INSTALL] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [INSTALL] Installing dependencies with correct versions...
echo This will take a few minutes...
echo.

REM Install in specific order to avoid conflicts
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo Installation encountered issues
    echo ========================================
    echo.
    echo Trying alternative method...
    echo.

    REM Try installing core packages first
    echo [INSTALL] Installing core AI packages...
    pip install "transformers>=4.35.0,<5.0.0" "sentence-transformers>=2.3.0"
    pip install "torch>=2.0.0"
    pip install "numpy>=1.24.0,<2.0" "pandas>=1.4,<2.0"

    echo.
    echo [INSTALL] Installing voice packages...
    pip install "discord.py[voice]>=2.3.0"
    pip install "TTS>=0.22.0"
    pip install "SpeechRecognition>=3.10.0"
    pip install "PyNaCl>=1.5.0"

    echo.
    echo [INSTALL] Installing remaining packages...
    pip install "faiss-cpu>=1.7.4" "scikit-learn>=1.3.0"
    pip install "nltk>=3.8.1" "spacy>=3.7.0"
    pip install "sounddevice>=0.4.6" "soundfile>=0.12.1"
    pip install "requests>=2.31.0" "python-dotenv>=1.0.0"
    pip install "colorama>=0.4.6" "tqdm>=4.66.0" "pyyaml>=6.0.1"
)

echo.
echo ========================================
echo [SUCCESS] Installation complete!
echo ========================================
echo.
echo Verifying key packages...
python -c "import discord; print('✓ Discord.py OK')"
python -c "import TTS; print('✓ TTS OK')"
python -c "import transformers; print('✓ Transformers OK')"
python -c "import sentence_transformers; print('✓ Sentence-Transformers OK')"
python -c "import pandas; print('✓ Pandas OK')"
python -c "import numpy; print('✓ Numpy OK')"

echo.
echo All packages installed successfully!
echo.
echo To start the bot:
echo - Run: start_bot.bat
echo   OR
echo - Run: python bot.py
echo.
pause
