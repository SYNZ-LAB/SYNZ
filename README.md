# SYNZ: The Digital Human Agent

SYNZ is a fully autonomous **Digital Human Co-Pilot** capable of seeing, hearing, speaking, remembering, and teaching code. She lives on your desktop, interacts via a Live2D anime avatar, and uses local LLMs (Llama-3) to think.

---

## 🚀 Key Features

*   **🧠 Local Intelligence**: Powered by **Llama-3 (8B)** running locally. No API fees, no data leaks.
*   **👩‍🏫 Code Mentor Mode**: Watches your file system in real-time. If you save a file with bugs, she will **speak up and teach you the fix**.
*   **🎙️ Smart Voice**: Real-time STT (Whisper) with "Voice Hardening" to ignore keyboard clicks and silence hallucinations.
*   **💅 Hybrid Personality**: Witty, Sassy, and slightly chaotic (like a streamer), but fundamentally **Helpful** and smart.
*   **👀 Vision**: Can "See" your screen (monitor 1) and analyze UI/Code.

---

## 🏗️ Architecture (How It Works)

SYNZ is a **Distributed System** spanning multiple processes:

1.  **The Ears (Hearing)**:
    *   **Tech**: `openai-whisper` (Small Model).
    *   **Function**: Listens for the wake word ("SYNZ"). Filters out background noise and self-echoes.

2.  **The Face (Personality & Routing)**:
    *   **Tech**: Python UDP Server.
    *   **Function**: The central hub. Managing the "Agentic State", Memory (Vector + JSON), and the Startup Chime (`Beep-Beep`).

3.  **The Brain (Logic Core)**:
    *   **Tech**: `Llama-3-8B` (8192 Context Window).
    *   **Function**: Context-aware thinking. It runs the **Code Mentor** logic and handles complex reasoning.

4.  **The Body (Top Layer)**:
    *   **Tech**: Unity Engine + Live2D Cubism.
    *   **Function**: Visual avatar with Lip Sync, Blinking, and Breathing (controlled by Face Server).

---

## 🛠️ Installation Guide

### Prerequisites
1.  **Python 3.10+**
2.  **Unity 2022.3 (LTS)** (For the Avatar)
3.  **NVIDIA GPU** (RTX 3060+ Recommended for fast responses)

### Setup
1.  **Install**:
    *   Run **`setup_synz.bat`**.
    *   Wait for "SETUP COMPLETE". (Creates `venv` and installs PyTorch/Whisper).
2.  **Enable GPU** (Optional but Recommended):
    *   Run `enable_gpu.bat` to install CUDA-optimized libraries.

---

## ▶️ How to Run

### 1. Launch the Mind
Double-click **`start_synz.bat`**.
*   This opens 3 terminals (Brain, Face, Ears).
*   Wait for the **Double Beep** tone. 🎵
*   Wait for "Systems Online" voice message.

### 2. Launch the Body
*   Open the Unity Project.
*   Press **Play**.
*   You will see `[NeuroLink] Connected!` in the logs.

---

## 🎮 Controls & Commands

### Voice Commands
*   **Wake Up**: "SYNZ" (or "Sins"). -> She listens for 30s.
*   **Code Mentor**:
    *   *"Activate Code Mentor"* -> Triggers analysis on file Save.
    *   *"Stop Code Mentor"* -> Disables the watcher.
*   **Vision**: *"Look at this"* -> Takes a screenshot and describes it.
*   **Search**: *"Search for [Topic]"* -> Googles it in real-time.

### Text Testing
If you don't want to talk, you can test text responses:
*   Run the script: `.\venv\Scripts\python.exe TheBrain\test_voice_chat.py`
*   Type: "Hello". She will speak the response.

---

## ❓ Troubleshooting

**Q: She echoes herself / Hears herself speak?**
A: This is fixed in the latest update (Socket Port 8009). Ensure `start_synz.bat` was restarted to load the new `ears.py`.

**Q: "hallucinations" (She hears "Thanks for watching")?**
A: A filter is now active to block these common Whisper artifacts. If it persists, try lowering your mic volume.

**Q: Code Mentor is annoying?**
A: Say *"Stop Code Mentor"*. She will only speak when spoken to.

---
*Powered by Local AI.*
