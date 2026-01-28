# SYNZ: The Digital Human Agent 🧠✨

SYNZ is a fully autonomous **Digital Human** capable of seeing, hearing, speaking, remembering, and writing code. She lives on your desktop, interacts via a Live2D anime avatar, and uses local LLMs (Llama-3) to think.

---

## 🏗️ How It Works (Architecture)

SYNZ is built as a **Distributed System** spanning multiple processes that talk to each other. This allows her to think, hear, and move simultaneously without lagging.

### 1. The Ears (Hearing) 👂
*   **Technology:** `openai-whisper` (Local).
*   **Function:** Listens to your microphone in real-time. uses VAD (Voice Activity Detection) to detect speech and transcribes it to text.
*   **Process:** Sends text to the *Face Server* via UDP.

### 2. The Face (Personality & Routing) 👤
*   **Technology:** Python, UDP Sockets.
*   **Function:** The central hub. It receives text, decides what to do (Answer? Search? Code?), and manages the "Agentic State".
*   **Features:**
    *   **Short Term Memory:** Remembers the last few minutes of conversation.
    *   **Tools:** Can trigger "The Hands" (Coding) or "The Eyes" (Vision).

### 3. The Brain (Logic Core) 🧠
*   **Technology:** `Llama-3-8B` (via `llama-cpp-python`).
*   **Function:** Pure intelligence. It receives a prompt ("Write a snake game") and generates the logic/code. It runs locally on your GPU/CPU.

### 4. The Body (Visualization) 💃
*   **Technology:** Unity Engine + Live2D Cubism.
*   **Function:** The visual avatar.
    *   **Lip Sync:** Moves mouth in sync with audio volume.
    *   **Expressions:** Blushes or changes eyes based on Emotion Tags sent by the Brain (e.g., `[HAPPY]`).

---

## 🛠️ Installation Guide

### Prerequisites
Before you start, ensure you have:
1.  **Python 3.10 or newer** installed and added to your System PATH.
2.  **Unity 2022.3 (LTS)** installed (if you want to run the Body yourself).
3.  **Live2D Cubism SDK** (Free Unity Package) imported into Unity.
4.  **A decent GPU** (NVIDIA RTX 3060 or better recommended) for fast Llama-3 inference.

### Step-by-Step Setup
1.  **Download the Project:**
    Clone this repository or extract the ZIP file to a folder (e.g., `C:\SYNZ`).

2.  **Run the Installer Script:**
    *   Navigate to the project folder.
    *   Double-click **`setup_synz.bat`**.
    *   **What it does:** It creates a hidden `venv` folder (Python Virtual Environment) and installs all the necessary AI libraries (PyTorch, Whisper, etc.).
    *   *Wait:* This may take 5-10 minutes depending on your internet speed. When it says "SETUP COMPLETE", close the window.

3.  **Unity Setup (The Body):**
    *   Open **Unity Hub** and add the project.
    *   Open the Scene.
    *   Ensure your Live2D Model (`.moc3`) is in the scene.
    *   Create an Empty GameObject named `"Setup"` and drag the **`SYNZ_Bootstrap.cs`** script (found in `unity_scripts/`) onto it.
    *   *Optional:* Build the project (`File -> Build Settings -> Build`) to creates a standalone `.exe` (e.g., `SYNZ_Body.exe`).

---

## 🚀 How to Run

### 1. Launch the Brain
Double-click **`start_synz.bat`**.
*   This will open **3 black terminal windows**. Do not close them!
    *   **Window 1 (The Brain):** Loads the LLM. Wait for "Model Online".
    *   **Window 2 (The Face):** Loads Personality. Wait for "Personality Loaded".
    *   **Window 3 (The Ears):** Listens to mic.
*   Once all 3 are ready, she is "Awake".

### 2. Launch the Body
*   **Option A:** Press **Play** in the Unity Editor.
*   **Option B:** Run your built `SYNZ_Body.exe`.
*   You should see `[NeuroLink] Connected!` in the logs/console.

---

## 🎮 Usage & Features

### The Wake Word
She is polite and won't listen until you address her.
*   **Say:** "SYNZ" (Pronounced "Sins").
*   **Result:** You will see a green light/log message. She is now listening for 30 seconds.

### Commands
Once awake, try these:

*   **Chat:** *"Hello! Who are you?"*
*   **Vision:** *"Look at this."* (She takes a screenshot of your main monitor and analyzes it).
*   **Search:** *"Search for the price of Bitcoin."* (She Googles it in real-time).
*   **Coding (Agentic Mode):**
    *   *"Write a python script called hello.py that prints hello."*
    *   *"Run hello.py."*
    *   If the code fails, she will **Self-Correct** (Reflex Loop) until it works.

---

## ⚠️ Troubleshooting

**Q: I get an error about "ChromaDB" or "Memory"?**
A: If you are on Python 3.14+, ChromaDB is disabled. We use a **JSON Fallback Memory** automatically. Just ignore the warning; she still remembers you!

**Q: She hears me but doesn't speak?**
A: Check if Unity is running. The audio plays through Unity. Also check your Volume Mixer.

**Q: The mouth doesn't move?**
A: Ensure the `SYNZ_Bootstrap.cs` script is in your Unity scene. It auto-wires the Lip Sync.
