@echo off
setlocal EnableDelayedExpansion
title Ledger - AI Currency Assistant

echo ======================================================================
echo   Ledger - AI Currency Assistant - Startup (Was made by Oleh Datsyk)
echo ======================================================================
echo.

REM ------------------------------------------------------------------
REM Step 0: Make sure we run from the folder this script lives in,
REM so double-clicking it from anywhere still works correctly.
REM ------------------------------------------------------------------
cd /d "%~dp0"

REM ------------------------------------------------------------------
REM Step 1: Check that Python is installed and available on PATH.
REM ------------------------------------------------------------------
echo [1/6] Checking for Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python was not found on your system.
    echo.
    echo Please install Python first:
    echo   1. Go to https://www.python.org/downloads/
    echo   2. Download and run the installer.
    echo   3. IMPORTANT: check the box "Add python.exe to PATH"
    echo      on the first screen of the installer.
    echo   4. Re-run this script after installing.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo       Found Python %PYVER%
echo.

REM ------------------------------------------------------------------
REM Step 2: Create the virtual environment if it doesn't exist yet.
REM ------------------------------------------------------------------
echo [2/6] Checking for virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo       No virtual environment found - creating one now...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Failed to create the virtual environment.
        echo Please check the messages above for details.
        echo.
        pause
        exit /b 1
    )
    echo       Virtual environment created.
) else (
    echo       Virtual environment already exists.
)
echo.

REM ------------------------------------------------------------------
REM Step 3: Activate the virtual environment.
REM ------------------------------------------------------------------
echo [3/6] Activating virtual environment...
call "venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Could not activate the virtual environment.
    echo.
    pause
    exit /b 1
)
echo       Activated.
echo.

REM ------------------------------------------------------------------
REM Step 4: Install / verify dependencies from requirements.txt.
REM Uses a marker file so we don't reinstall every single launch.
REM ------------------------------------------------------------------
echo [4/6] Checking dependencies...
if not exist "requirements.txt" (
    echo.
    echo [ERROR] requirements.txt was not found in this folder.
    echo Make sure this script sits in the same folder as app.py.
    echo.
    pause
    exit /b 1
)

set NEED_INSTALL=0
if not exist "venv\.deps_installed" (
    set NEED_INSTALL=1
) else (
    fc /b "requirements.txt" "venv\.deps_installed" >nul 2>nul
    if %errorlevel% neq 0 set NEED_INSTALL=1
)

if !NEED_INSTALL! equ 1 (
    echo       Installing missing dependencies - this may take a minute...
    python -m pip install --upgrade pip >nul 2>nul
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo.
        echo [ERROR] Failed to install dependencies. See messages above.
        echo.
        pause
        exit /b 1
    )
    copy /y "requirements.txt" "venv\.deps_installed" >nul 2>nul
    echo       Dependencies installed.
) else (
    echo       Dependencies already up to date.
)
echo.

REM ------------------------------------------------------------------
REM Step 5: Verify the .env file exists.
REM ------------------------------------------------------------------
echo [5/6] Checking for .env configuration file...
if not exist ".env" (
    if exist ".env.example" (
        echo       No .env file found - creating one from .env.example...
        copy /y ".env.example" ".env" >nul
        echo.
        echo       A new .env file was created for you.
        echo       IMPORTANT: open .env in a text editor and add your
        echo       real API keys before using the AI-powered features.
        echo       See INSTRUCTION.md for step-by-step help.
        echo.
    ) else (
        echo.
        echo [WARNING] No .env or .env.example file was found.
        echo The app will start, but AI-powered features will not work
        echo until you create a .env file with your API keys.
        echo See INSTRUCTION.md for details.
        echo.
    )
) else (
    echo       .env file found.
)
echo.

REM ------------------------------------------------------------------
REM Step 6: Launch the application.
REM ------------------------------------------------------------------
echo [6/6] Starting the application...
echo.
echo ============================================================
echo   Once you see "Running on http://127.0.0.1:1000" below,
echo   open that address in your web browser to use the app.
echo   Press CTRL+C in this window to stop the server.
echo ============================================================
echo.

python app.py

REM ------------------------------------------------------------------
REM If the app exits (crashes or is stopped), keep the window open
REM so the user can read any error messages instead of it vanishing.
REM ------------------------------------------------------------------
echo.
echo ============================================================
echo   The application has stopped.
if %errorlevel% neq 0 (
    echo   It looks like it exited with an error - scroll up to see
    echo   the details, or check INSTRUCTION.md's Troubleshooting
    echo   section for help with common problems.
)
echo ============================================================
echo.
pause
