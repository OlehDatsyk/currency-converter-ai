#!/bin/bash

# ============================================================
#  Ledger - AI Currency Assistant - Startup (macOS)
#  Double-click this file in Finder to run it.
#  (First time only: see INSTRUCTION.md if macOS blocks it
#   from running due to Gatekeeper / "unidentified developer".)
# ============================================================

# Always run from the folder this script lives in, so double-clicking
# it from Finder works no matter where the project folder is.
cd "$(dirname "$0")" || exit 1

echo "======================================================================"
echo "  Ledger - AI Currency Assistant - Startup (Was made by Oleh Datsyk)"
echo "======================================================================"
echo ""

# ------------------------------------------------------------------
# Step 1: Check that Python 3 is installed and available.
# ------------------------------------------------------------------
echo "[1/6] Checking for Python..."

PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "[ERROR] Python was not found on your system."
    echo ""
    echo "Please install Python first:"
    echo "  1. Go to https://www.python.org/downloads/"
    echo "  2. Download and run the macOS installer (.pkg file)."
    echo "  3. Click through the installer with the default options."
    echo "  4. Re-run this script after installing."
    echo ""
    read -n 1 -s -r -p "Press any key to close this window..."
    exit 1
fi

PYVER=$("$PYTHON_CMD" --version 2>&1)
echo "      Found $PYVER"
echo ""

# ------------------------------------------------------------------
# Step 2: Create the virtual environment if it doesn't exist yet.
# ------------------------------------------------------------------
echo "[2/6] Checking for virtual environment..."
if [ ! -f "venv/bin/activate" ]; then
    echo "      No virtual environment found - creating one now..."
    "$PYTHON_CMD" -m venv venv
    if [ $? -ne 0 ]; then
        echo ""
        echo "[ERROR] Failed to create the virtual environment."
        echo "Please check the messages above for details."
        echo ""
        read -n 1 -s -r -p "Press any key to close this window..."
        exit 1
    fi
    echo "      Virtual environment created."
else
    echo "      Virtual environment already exists."
fi
echo ""

# ------------------------------------------------------------------
# Step 3: Activate the virtual environment.
# ------------------------------------------------------------------
echo "[3/6] Activating virtual environment..."
# shellcheck disable=SC1091
source "venv/bin/activate"
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Could not activate the virtual environment."
    echo ""
    read -n 1 -s -r -p "Press any key to close this window..."
    exit 1
fi
echo "      Activated."
echo ""

# ------------------------------------------------------------------
# Step 4: Install / verify dependencies from requirements.txt.
# Uses a marker file so we don't reinstall on every single launch.
# ------------------------------------------------------------------
echo "[4/6] Checking dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo ""
    echo "[ERROR] requirements.txt was not found in this folder."
    echo "Make sure this script sits in the same folder as app.py."
    echo ""
    read -n 1 -s -r -p "Press any key to close this window..."
    exit 1
fi

NEED_INSTALL=0
if [ ! -f "venv/.deps_installed" ]; then
    NEED_INSTALL=1
elif ! diff -q "requirements.txt" "venv/.deps_installed" >/dev/null 2>&1; then
    NEED_INSTALL=1
fi

if [ "$NEED_INSTALL" -eq 1 ]; then
    echo "      Installing missing dependencies - this may take a minute..."
    pip install --upgrade pip >/dev/null 2>&1
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "[ERROR] Failed to install dependencies. See messages above."
        echo ""
        read -n 1 -s -r -p "Press any key to close this window..."
        exit 1
    fi
    cp "requirements.txt" "venv/.deps_installed"
    echo "      Dependencies installed."
else
    echo "      Dependencies already up to date."
fi
echo ""

# ------------------------------------------------------------------
# Step 5: Verify the .env file exists.
# ------------------------------------------------------------------
echo "[5/6] Checking for .env configuration file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "      No .env file found - creating one from .env.example..."
        cp ".env.example" ".env"
        echo ""
        echo "      A new .env file was created for you."
        echo "      IMPORTANT: open .env in a text editor and add your"
        echo "      real API keys before using the AI-powered features."
        echo "      See INSTRUCTION.md for step-by-step help."
        echo ""
    else
        echo ""
        echo "[WARNING] No .env or .env.example file was found."
        echo "The app will start, but AI-powered features will not work"
        echo "until you create a .env file with your API keys."
        echo "See INSTRUCTION.md for details."
        echo ""
    fi
else
    echo "      .env file found."
fi
echo ""

# ------------------------------------------------------------------
# Step 6: Launch the application.
# ------------------------------------------------------------------
echo "[6/6] Starting the application..."
echo ""
echo "============================================================"
echo "  Once you see \"Running on http://127.0.0.1:1000\" below,"
echo "  open that address in your web browser to use the app."
echo "  Press CTRL+C in this window to stop the server."
echo "============================================================"
echo ""

python app.py
APP_EXIT_CODE=$?

# ------------------------------------------------------------------
# If the app exits (crashes or is stopped), keep the window open
# so the user can read any error messages instead of it vanishing.
# ------------------------------------------------------------------
echo ""
echo "============================================================"
echo "  The application has stopped."
if [ $APP_EXIT_CODE -ne 0 ]; then
    echo "  It looks like it exited with an error - scroll up to see"
    echo "  the details, or check INSTRUCTION.md's Troubleshooting"
    echo "  section for help with common problems."
fi
echo "============================================================"
echo ""
read -n 1 -s -r -p "Press any key to close this window..."
