# Project Lilith

**Project Lilith** is a local-first, agentic AI co-worker for Game Developers. It consists of three main components:

1.  **The Brain**: A custom PyTorch SLM (Small Language Model) ~150M parameters, trained on C#/C++ code.
2.  **The Watcher**: A lightweight C++ background service that monitors Unity/Unreal logs for errors.
3.  **The Body**: A transparent Unity overlay that acts as the VTuber interface, connecting to VTube Studio.

## Directory Structure

- `TheBrain/`: Python code for the SLM (Model, Tokenizer, Training).
- `TheWatcher/`: C++ code for the log monitor.
- `TheBody/`: C# scripts for the Unity overlay.

## Setup

### The Brain
1.  Install dependencies: `pip install -r TheBrain/requirements.txt`
2.  Train Tokenizer: `python TheBrain/tokenizer.py --data_dir <path_to_code>`
3.  Train Model: `python TheBrain/train.py`

### The Watcher
1.  Compile `TheWatcher/main.cpp` (requires `ws2_32` lib on Windows).
    ```bash
    g++ TheWatcher/main.cpp -o watcher.exe -lws2_32
    ```
2.  Run `watcher.exe`.

### The Body
1.  Copy `TheBody/*.cs` to your Unity Project's `Assets/Scripts` folder.
2.  Attach `LilithOverlay.cs` to a GameObject.
3.  Configure VTube Studio settings.

## License
Open Source.
