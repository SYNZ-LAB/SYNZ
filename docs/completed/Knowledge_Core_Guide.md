# Phase 8: Awakening the Logic Core (The Brain)

Right now, **SYNZ** is just a "Face" (Python). She talks, but she doesn't *think* deeply.
To give her **Knowledge**, we need to turn on the **C++ Core**.

---

## 🏗️ Step 1: Download the Model
We need a GGUF model file (the actual brain weights). We recommend `Qwen2.5-Coder` for coding skills.

1.  **Download this file**: [Qwen2.5-Coder-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf)
2.  **Create folder**: `SYNZ/models`
3.  **Place file**: Save it as `SYNZ/models/Qwen2.5-Coder-1.5B-Instruct-GGUF.gguf`

---

## 🛠️ Step 2: Compile the Core
We need to build `synz_core.exe` using CMake.

**Terminal 2 (PowerShell):**
```powershell
cd "C:\Users\Adminb\OneDrive\Documents\Projects\SYNZ"

# 1. Configure (Generate Build Files)
cmake -S . -B build

# 2. Compile (Build the Exe)
cmake --build build --config Release
```
*(This will create `build/Release/synz_core.exe`)*

---

## 🚀 Step 3: Dual-Process Launch
You need **TWO** terminals running at the same time.

### Terminal A (The Brain - Logic) 🧠
This runs the Heavy C++ AI.
```powershell
cd "C:\Users\Adminb\OneDrive\Documents\Projects\SYNZ"
.\build\Release\synz_core.exe
```
*Wait for it to say: "[SYNZ] Logic Bridge Open on Port 8006"*

### Terminal B (The Face - Personality) 👧
This runs the Python Sass & Voice.
```powershell
cd "C:\Users\Adminb\OneDrive\Documents\Projects\SYNZ"
.\venv\Scripts\python.exe -u TheBrain\face_server.py
```
*Wait for it to say: "[THE SELF] Awakening..."*

---

## 🧪 Step 4: Verification
Now, talk to her in Terminal B (or via Unity).

**Type:** `Can you write a bubble sort in Python?`

1.  **Face (Python)**: Sees "code" keyword.
2.  **Face**: Sends request to **Core (Port 8006)**.
3.  **Core (C++)**: Thinks... Generates code... Sends back.
4.  **Face**: Wraps it in Sass ("Ugh, fine. Here is your code.").
5.  **Voice**: Speaks the response.

**Goal Achieved:** A Hybrid AI that is Sassy (Python) but Smart (C++).
