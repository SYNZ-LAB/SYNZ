@echo off
:: Ensures script runs from its own directory
cd /d "%~dp0"
title SYNZ Launcher
echo ==========================================
echo       SYNZ GOD-MODE LAUNCHER 🚀
echo ==========================================
echo.
echo [1/3] Launching Core (Llama-3 Python)...
start "SYNZ Core (Brain)" /min cmd /k "venv\Scripts\python.exe -u TheBrain\brain_server.py"

echo [2/3] Launching Face (Python)...
start "SYNZ Face (Main)" cmd /k "venv\Scripts\python.exe -u TheBrain\face_server.py"

echo [3/3] Launching Ears (Whisper)...
start "SYNZ Ears (Mic)" /min cmd /k "venv\Scripts\python.exe -u TheBrain\ears.py"



echo.
echo [4/5] Launching Body...
if exist "Build\SYNZ_Body.exe" (
    echo     - Found Standalone Build. Launching...
    start "" "Build\SYNZ_Body.exe"
) else (
    echo     - No build found. Please press PLAY in Unity Editor.
)

echo.
echo All systems go! 
echo Check the 'SYNZ Face' window for the main interaction.
echo.
timeout /t 5
exit
