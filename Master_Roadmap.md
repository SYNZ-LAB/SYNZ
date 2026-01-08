# Project Lilith: Master Status & Roadmap 🚀

This document tracks the overall progress of Project Lilith, an Agentic AI Co-worker.

## 🟢 Completed Features (Live & Working)

### 🧠 The Brain (Intelligence)
- [x] **Custom SLM Architecture**: PyTorch-based Transformer model (~1M parameters).
- [x] **Personality System**:
    - [x] `personality.py`: Loads profiles (Default, Tsundere) from JSON.
    - [x] **Frustration Logic**: Tracks error frequency; turns "ANGRY" if errors spike >0.8 intensity.
- [x] **Training Data**: Contrast pairs for error inputs (e.g., `[PERSONALITY:TSUNDERE]` -> `ACTION_ANGRY`).
- [x] **Tokenizer**: Custom BPE trained on error logs and personality tags.
- [x] **Inference Server**: UDP Listener for the Watcher, forwarding actions to the Body.

### 👁️ The Watcher (Perception)
- [x] **Log Monitoring**: Reads `Editor.log` in real-time using Windows API (`ReadDirectoryChangesW`).
- [x] **Error Detection**: Regex/String matching for `NullReferenceException`, `Segmentation Fault`, etc.
- [x] **Context Awareness (Phase 2)**:
    - [x] **Sliding Window Buffer**: Keeps the last 5 lines of history in memory.
    - [x] **Context Payload**: Sends the full 5-line context block to the Brain via UDP.

### 💃 The Body (Visuals)
- [x] **Unity Overlay**: Transparent, click-through window overlaying the desktop.
- [x] **VTube Studio Integration**: Triggers expressions via WebSocket.
- [x] **Reactive Mood (Phase 3)**:
    - [x] **Mood Colors**: Changes UI aura/glow color (`UpdateUIMood`).
    - [x] **Thinking Pulse**: "Breathing" animation while inference runs (`isThinking` state).

---

## 🟡 In Progress / Next Up

### 🧠 Brain Enhancements
- [ ] **Short-Term Memory**: Remember context across *multiple* distinct errors (not just immediate lines).
- [ ] **Code Context Injection**: Parse the specific *file path* from the error to know exactly where to look.

### 💃 Body Polish (Aesthetics)
- [ ] **Glassmorphism UI**: Upgrade the simple colored glow to a premium frosted-glass shader.
- [ ] **Chat Bubble**: A sleek UI element showing Lilith's internal monologue text.

---

## 🔮 Future Backlog (Planned)

### 🗣️ Voice & Interaction
- [ ] **Local TTS**: Integrate `Piper` or `Coqui` so Lilith speaks her reactions.
- [ ] **Voice Input**: Allow the user to "talk back" to Lilith via microphone.

### 🛠️ Agentic Capabilities (The "Co-worker" Part)
- [ ] **Auto-Open Script**: If a file path is detected in the error log, send a command to open VS Code to that line.
- [ ] **Documentation Search**: Automatically query Unity docs for the specific error code.
- [ ] **Git Blame**: If a build breaks, check `git log` to see who committed the breaking change (and scold them if it's you!).

### ⚙️ Optimization
- [ ] **Performance Monitor**: Watcher tracks CPU/RAM usage and complains if the editor gets sluggish.
