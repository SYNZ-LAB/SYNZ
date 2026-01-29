@echo off
:: Ensures script runs from its own directory
cd /d "%~dp0"
title SYNZ GPU Activator 🚀
echo ==========================================
echo       SYNZ GPU ACTIVATOR (NVIDIA)
echo ==========================================
echo.
echo [1/3] Uninstalling CPU libraries...
call venv\Scripts\pip uninstall -y torch torchvision torchaudio llama-cpp-python

echo.
echo [2/3] Installing PyTorch with CUDA 12.4...
:: Using Stable PyTorch 2.5.1 with CUDA 12.4
call venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo.
echo [3/3] Installing Llama-3 with CUDA Support...
:: Use pre-built wheel to avoid compiling (requires heavy CUDA Toolkit)
call venv\Scripts\pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124

echo.
echo ==========================================
echo [SUCCESS] GPU Mode Enabled! 🟢
echo You can now run start_synz.bat
echo ==========================================
pause
