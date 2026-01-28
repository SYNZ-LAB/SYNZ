# SYNZ: Digital Human Agent

An agentic AI that can see, hear, speak, and write code.

## Prerequisites

1.  **Python 3.10+** (Ensure it is added to PATH).
2.  **Unity 2022.3+** (For the visual body).
3.  **Live2D Cubism SDK** (Unity Package).
4.  **Hardware:** NVIDIA GPU recommended for Llama-3 inference.

## Installation

1.  **Run Installer:**
    Double-click `setup_synz.bat` in the root directory.
    This script will:
    - Create a Python virtual environment (venv).
    - Install all required Python dependencies (PyTorch, Transformers, Whisper, etc.).
    - Configure the project for local execution.

    *Note: The C++ build step has been disabled in favor of a Python-based Logic Core to ensure compatibility across different Windows environments.*

2.  **Unity Setup:**
    - Open the `unity_scripts` folder.
    - Copy all `.cs` files into your Unity Project's `Assets` folder.
    - Create an Empty GameObject in your scene named "Setup".
    - Attach the `SYNZ_Bootstrap.cs` script to this object.
    - Ensure your Live2D model is in the scene.
    - Press Play to verify the "SYNZ_NeuroLink" connection.

## How to Run

1.  **Start the Brain:**
    Double-click `start_synz.bat`.
    This will open three terminal windows:
    - **Core:** The Logic Engine (Llama-3).
    - **Face:** The Personality & Tool Router.
    - **Ears:** The Microphone Listener (Whisper).

    Wait until the Face window displays "Personality Loaded" and the Brain window displays "Model Online".

2.  **Start the Body:**
    Run your Unity Scene (Editor Play Mode or Built Executable).
    The Agent is now fully active.

## Usage

**Wake Word:**
The agent listens for the keyword "SYNZ" (pronounced "Sins").
When heard, it wakes up for 30 seconds.

**Voice Commands:**
-   **Conversation:** "Hello, who are you?"
-   **Coding:** "Write a Python script called game.py that prints hello world."
-   **Execution:** "Run game.py."
-   **Vision:** "Look at this." (Takes a screenshot).
-   **Search:** "Search for the latest stock prices."

## Troubleshooting

-   **Crash on Startup:** Ensure `setup_synz.bat` completed successfully.
-   **No Voice:** Check that Unity is running and the AudioSource volume is up.
-   **Connection Failed:** Ensure no other program is using ports 8005 or 8006.
