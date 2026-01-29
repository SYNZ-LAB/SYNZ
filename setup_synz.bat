@echo off
:: Ensures script runs from its own directory
cd /d "%~dp0"
title SYNZ Installer
echo ==========================================
echo       SYNZ INSTALLER & BUILDER 🛠️
echo ==========================================
echo.

:: 0. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and tick "Add to PATH".
    pause
    exit /b 1
)

:: 1. Python Environment
echo [1/3] Setting up Python Environment...
if not exist "venv" (
    echo     - Creating venv...
    python -m venv venv
)
echo     - Upgrading pip...
call venv\Scripts\python.exe -m pip install --upgrade pip
echo     - Installing dependencies...
call venv\Scripts\pip install -r TheBrain\requirements.txt

:: 2. C++ Build (DISABLED - USING PYTHON BRAIN)
echo.
echo [2/3] Skipping C++ Build (Native Core). Using Python Fallback.

echo.
echo [3/3] Verify...
echo Ready to launch Python Brain.

echo.
echo ==========================================
echo       SETUP COMPLETE! 🍰
echo       Run 'start_synz.bat' to launch.
echo ==========================================
pause
