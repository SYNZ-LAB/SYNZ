@echo off
title SYNZ Installer
echo ==========================================
echo       SYNZ INSTALLER & BUILDER 🛠️
echo ==========================================
echo.

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
:: if not exist "build" mkdir build
:: cd build
:: cmake ..
:: cmake --build . --config Release
:: cd ..

echo.
echo [3/3] Verify...
echo Ready to launch Python Brain.

echo.
echo ==========================================
echo       SETUP COMPLETE! 🍰
echo       Run 'start_synz.bat' to launch.
echo ==========================================
pause
