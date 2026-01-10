# Project SYNZ (SYNZ Core)

**SYNZ** (Systemic Yield Neural Zenith) is a local-first, zero-latency Agentic AI Co-worker built in **Native C++**.

Unlike typical AI assistants that rely on Python APIs and heavy latency, SYNZ runs as a single compiled executable ("The Monolith"), integrating standard file monitoring with direct embedded LLM inference.

## Architecture: The Native Architect

1.  **The Sentinel**: A `std::filesystem` watcher that polls development logs (Unity/Unreal) with sub-millisecond precision.
2.  **The Brain**: Embedded `llama.cpp` instance running quantized Expert Models (1.5B - 7B parameters) directly on the GPU.
3.  **The Interlink**: Zero-copy memory architecture. Log strings are passed directly to the inference context.

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
