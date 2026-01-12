# Project SYNZ (SYNZ Core)

# SYNZ: The Dual-Brain Agent 🧠🤖

SYNZ is a local-first, agentic co-worker for Unity Developers.
It uses a **Hybrid Architecture** to combine raw coding power with a custom personality.

## The Architecture
1.  **SYNZ Core (Left Brain)**:
    *   **Engine**: C++ Native (`synz_core.exe`)
    *   **Model**: Qwen 2.5-Coder (1.5B/7B)
    *   **Role**: Logic, Coding, Error Fixing.
2.  **SYNZ Face (Right Brain)**:
    *   **Engine**: Python Custom Transformer (`NanoSYNZ`)
    *   **Model**: Trained from scratch on your chat logs.
    *   **Role**: Personality, Chat, VTuber Control.

## Quick Start

### 1. The Core (Logic)
```powershell
mkdir build
cd build
cmake ..
cmake --build . --config Release
.\Release\synz_core.exe
```

### 2. The Face (Personality)
```powershell
# Install Restrictions: Python 3.12 Recommended (3.14 works on CPU only)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install torch
python TheBrain/train_scratch.py
```

## Prerequisites

- **CMake** (3.14+)
- **C++ Compiler** (MSVC / GCC / Clang) supporting C++17.
- **CUDA Toolkit** (Optional, for NVIDIA GPU acceleration).

## Building "SYNZ Core"

This project uses `CMake` to manage dependencies (like `llama.cpp`) automatically.

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

## Setup

1.  Download a GGUF model (e.g., `DeepSeek-Coder-V2-Lite-Instruct.Q4_K_M.gguf`) to the `models/` folder.
2.  Edit `src/main.cpp` to point to your target log file.
3.  Run `synz_core.exe`.

## 🤝 Team Workflow

SYNZ uses a **Hybrid Architecture** to separate *Training* from *Inference*.

### 🔵 For Data Scientists (Python)
*   **Where**: `TheBrain/` folder.
*   **Role**: "Train the Mind".
*   **Tasks**:
    *   Fine-tune `.gguf` models using `Unsloth` / PyTorch.
    *   Process documentation datasets.
    *   **Goal**: Output better `.gguf` files for the Core team.

### 🟢 For Systems Engineers (C++)
*   **Where**: `src/` folder.
*   **Role**: "Build the Body".
*   **Tasks**:
    *   Optimize `synz_core` performance and Unity IPC.
    *   Implement new Llama.cpp features (Flash Attention, etc).
    *   **Goal**: Reduce latency to 0ms.

## License
Open Source.
