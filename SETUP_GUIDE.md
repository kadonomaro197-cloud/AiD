# 🚀 AiD Setup Guide - One-Time Installation

This guide will help you set up AiD's dependencies **once** so they persist in your virtual environment.

---

## ✅ Quick Setup (Recommended)

### **Windows Users** (You!):

1. **Double-click `setup.bat`**
   - This creates/activates your virtual environment
   - Installs all dependencies from `requirements.txt`
   - One-time process!

2. **Start the bot** (every time):
   - Double-click `start_bot.bat`
   - Or manually: `venv\Scripts\activate.bat` → `python bot.py`

### **Linux/Mac Users**:

```bash
# One-time setup
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start bot (every time)
source venv/bin/activate
python bot.py
```

---

## 🔧 Manual Setup (If Automated Fails)

### Step 1: Create Virtual Environment

```bash
# Windows
python -m venv venv

# Linux/Mac
python3 -m venv venv
```

### Step 2: Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Fix Version Conflicts (If Needed)

If you get the `NLTK_IMPORT_ERROR`, run:

```bash
pip install --upgrade transformers sentence-transformers
```

Or force compatible versions:

```bash
pip install transformers==4.36.0 sentence-transformers==2.3.1
```

---

## 🛠️ System-Level Dependencies

Some packages require system-level tools:

### **FFmpeg** (Required for Discord Voice)

**Windows**:
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH:
   - Search "Environment Variables" in Start Menu
   - Edit "Path" variable
   - Add `C:\ffmpeg\bin`
   - Restart terminal

**Linux**:
```bash
sudo apt-get install ffmpeg
```

**Mac**:
```bash
brew install ffmpeg
```

### **PyAudio** (Optional - for local STT)

**Windows**:
- May need Microsoft C++ Build Tools
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Or use pre-built wheel: `pip install pipwin && pipwin install pyaudio`

**Linux**:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Mac**:
```bash
brew install portaudio
pip install pyaudio
```

---

## 🎯 Understanding Virtual Environments

### **Why Virtual Environments?**

Virtual environments keep your Python packages isolated per project:

- ✅ Packages installed **once** in the venv
- ✅ Persist across bot restarts
- ✅ Don't interfere with other Python projects
- ✅ Can be recreated if corrupted

### **How It Works**:

```
Your Computer
├── Python (system-wide)
├── AiD Project
│   ├── venv/
│   │   ├── Lib/site-packages/  ← All dependencies installed HERE
│   │   └── Scripts/activate.bat
│   ├── bot.py
│   └── requirements.txt
```

When you activate the venv:
- Python uses packages from `venv/Lib/site-packages/`
- Packages stay there **permanently** until you delete the venv

### **Important**:

You need to **activate the venv** every time you:
- Open a new terminal
- Restart your computer
- Close and reopen your terminal

But you **DON'T** need to reinstall packages each time!

---

## 📋 Verification Checklist

After setup, verify everything works:

```bash
# 1. Activate venv
venv\Scripts\activate.bat  # Windows
# OR
source venv/bin/activate  # Linux/Mac

# 2. Check Python packages
pip list | grep discord
pip list | grep TTS
pip list | grep transformers
pip list | grep sentence-transformers

# 3. Test imports
python -c "import discord; print('Discord OK')"
python -c "import TTS; print('TTS OK')"
python -c "from transformers import pipeline; print('Transformers OK')"
python -c "from sentence_transformers import SentenceTransformer; print('Sentence-Transformers OK')"

# 4. Start the bot
python bot.py
```

---

## ⚠️ Common Issues & Fixes

### **Issue 1**: "NLTK_IMPORT_ERROR" (Your Current Error)

**Cause**: Version conflict between `transformers` and `sentence-transformers`

**Fix**:
```bash
pip install --upgrade transformers sentence-transformers
```

### **Issue 2**: "pip: command not found"

**Cause**: Python not in PATH or venv not activated

**Fix**:
```bash
# Make sure venv is activated
venv\Scripts\activate.bat  # You should see (venv) in prompt

# Try:
python -m pip install -r requirements.txt
```

### **Issue 3**: "No module named 'discord'"

**Cause**: Venv not activated OR packages not installed

**Fix**:
```bash
# 1. Activate venv
venv\Scripts\activate.bat

# 2. Reinstall
pip install -r requirements.txt
```

### **Issue 4**: PyAudio installation fails

**Cause**: Missing C++ compiler on Windows

**Fix (Option 1)**: Use pipwin
```bash
pip install pipwin
pipwin install pyaudio
```

**Fix (Option 2)**: Install from pre-built wheel
1. Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Install: `pip install PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl` (adjust version)

**Fix (Option 3)**: Skip PyAudio
- STT will still work with other backends
- PyAudio is optional for local microphone input

### **Issue 5**: FFmpeg not found

**Cause**: FFmpeg not installed or not in PATH

**Fix**:
```bash
# Windows: Download and add to PATH (see above)
# Linux:
sudo apt-get install ffmpeg

# Verify:
ffmpeg -version
```

---

## 🔄 Updating Dependencies

If you need to update packages later:

```bash
# Activate venv
venv\Scripts\activate.bat

# Update single package
pip install --upgrade discord.py

# Update all packages
pip install --upgrade -r requirements.txt

# Update transformers specifically (common need)
pip install --upgrade transformers sentence-transformers
```

---

## 🗑️ Resetting Everything (Nuclear Option)

If your venv gets corrupted or you want a fresh start:

```bash
# 1. Delete venv folder
rmdir /s venv  # Windows
# OR
rm -rf venv  # Linux/Mac

# 2. Re-run setup
setup.bat  # Windows
# OR
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt  # Linux/Mac
```

---

## 🎯 Daily Workflow

### **First Time** (One-time):
```bash
setup.bat  # Install everything
```

### **Every Time You Start AiD**:
```bash
start_bot.bat  # Activates venv + starts bot
```

### **Manual Method** (Every time):
```bash
venv\Scripts\activate.bat  # Activate venv
python bot.py              # Start bot
```

**That's it!** Once installed, packages persist in your venv.

---

## 📞 Still Having Issues?

If setup still fails, share:
1. Your Python version: `python --version`
2. Operating system
3. Full error message
4. Output of: `pip list`

Common troubleshooting:
- Make sure Python 3.9+ is installed
- Run terminal as Administrator (Windows)
- Check antivirus isn't blocking pip
- Verify internet connection for package downloads

---

## ✅ Summary

**Key Points**:
1. Virtual environments persist - install once, use forever
2. Always activate venv before running bot: `venv\Scripts\activate.bat`
3. Use `setup.bat` for easy initial setup
4. Use `start_bot.bat` for easy bot startup
5. Fix version conflicts: `pip install --upgrade transformers sentence-transformers`

**You're all set!** 🎉
