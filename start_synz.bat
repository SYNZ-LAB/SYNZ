@echo off
title SYNZ Launcher
echo ==========================================
echo       SYNZ GOD-MODE LAUNCHER 🚀
echo ==========================================
echo.
echo [1/3] Launching Core (Llama-3)...
start "SYNZ Core (C++)" /min cmd /k "build\Release\synz_core.exe"

echo [2/3] Launching Face (Python)...
start "SYNZ Face (Main)" cmd /k "venv\Scripts\python.exe -u TheBrain\face_server.py"

echo [3/3] Launching Ears (Whisper)...
start "SYNZ Ears (Mic)" /min cmd /k "venv\Scripts\python.exe -u TheBrain\ears.py"

echo.
echo All systems go! 
echo Check the 'SYNZ Face' window for the main interaction.
echo.
timeout /t 5
exit
