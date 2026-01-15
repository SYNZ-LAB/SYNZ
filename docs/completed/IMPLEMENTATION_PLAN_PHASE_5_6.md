# Implementation Plan - Native Embedded Architect (SYNZ Core)

## Goal Description
Build a **Dual-Model Agentic System**:
1.  **Interaction Layer**: A custom SLM (trained by us) for personality.
2.  **Expert Layer**: Qwen 2.5 (C++ Native) for coding support.
The current task is to implement the **Expert Layer (Qwen)** in C++.

## User Review Required
> [!IMPORTANT]
> This is a complete rewrite of the backend. The Python code (`TheBrain/`) is now legacy.
> You must have `cmake` installed to build the new core.

## Proposed Changes

### 1. The Build System
#### [NEW] [CMakeLists.txt](file:///c:/Users/Adminb/OneDrive/Documents/Projects/SYNZ/CMakeLists.txt)
- **Dependency Management**: Use `FetchContent` to download and build `llama.cpp` from source.
- **Configuration**: Enable `LLAMA_CUBLAS` (CUDA) by default for performance.

### 2. The Source Code
#### [NEW] [src/main.cpp](file:///c:/Users/Adminb/OneDrive/Documents/Projects/SYNZ/src/main.cpp)
- **LogMonitor Class**:
    - Replaces `ReadDirectoryChangesW` with portable `std::filesystem` polling.
    - Captures "Context" (last 5 lines) into `std::vector<string>`.
- **LlamaEngine Class**:
    - Wraps the `llama.h` C API.
    - Manages `llama_model` (VRAM) and `llama_context` (KV Cache).
    - `Infer(string)`: Directly tokenizes and processes log data.

### 3. Verification Plan

#### Manual Verification
1.  **Build**: Run `cmake --build . --config Release`.
2.  **Test**: 
    - Create a dummy `test.log`.
    - Run `synz_core.exe` and verify "NeuroLink Waiting" message.
  - Verify `llama.cpp` loads Qwen model (The Engineer).

## Phase 4: Training "The Face" (Custom SLM)
> [!NOTE]
> This is where your GPU is used. We use the C++ Core to RUN the model, but we use Python to TRAIN it.
-   **Goal**: Create a small, fast model (approx 500M params) that is purely for personality and chatting.
-   **Tech**: PyTorch + LoRA (Low-Rank Adaptation) or Full Fine-Tune.
-   **Integration**: After training, we convert it to `.gguf` and load it into SYNZ Core alongside Qwen.
    - Append "NullReferenceException" to `test.log`.
    - Verify that `synz_core` outputs a generated fix/response to the console within 100ms.

## Phase 5: Reinforcement Loop (RL-Lite)
### The Face (Python)
#### [MODIFY] [face_server.py](file:///C:/Users/Adminb/OneDrive/Documents/Projects/SYNZ/TheBrain/face_server.py)
*   [ ] Add `ConversationHistory` list.
*   [ ] Add `!good` handler to append history to `data/training_data.txt`.
*   [ ] Add `!bad` handler (optional, acts as Undo).

## Verification Plan
### Manual Verification
*   Start `face_server.py`.
*   Chat with it.
*   Type `!good`.
*   Check `data/training_data.txt` to see if the interaction was saved.
