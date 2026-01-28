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

:: 2. C++ Build
echo.
echo [2/3] Building C++ Core...
if not exist "build" mkdir build
cd build
echo     - Configuring CMake...
cmake ..
if %errorlevel% neq 0 (
    echo [ERR] CMake Configuration Failed! Do you have CMake installed?
    pause
    exit /b %errorlevel%
)
echo     - Compiling (Release Mode)...
cmake --build . --config Release
cd ..

echo.
echo [3/3] Verify...
if exist "build\Release\synz_core.exe" (
    echo [SUCCESS] synz_core.exe created.
) else (
    echo [WARN] synz_core.exe missing. Build might have failed.
)

echo.
echo ==========================================
echo       SETUP COMPLETE! 🍰
echo       Run 'start_synz.bat' to launch.
echo ==========================================
pause
