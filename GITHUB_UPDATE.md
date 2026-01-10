# SYNZ Project Update Log

## Commit 1 (2026-01-11)
### Native C++ Agentic Architecture Update

**Concept**: Transitioning from a distributed Python/UDP system to a high-performance **Native C++ Monolith** ("SYNZ Core") with a **Dual-Brain Hybrid Architecture**.

## 🚀 Key Changes

### 1. The Core (Native C++)
*   **Monolithic Engine**: Implemented `synz_core` (C++17) to replace the external Python inference server, achieving **Zero Latency** communication.
*   **Embedded LLM**: Integrated `llama.cpp` directly into the executable via CMake `FetchContent`.
*   **Qwen 2.5 Coding Expert**: Standardized on `Qwen2.5-Coder-1.5B-Instruct` as the "Engineer" model, enabling real-time C# analysis and error correction.
*   **Manual Inference Loop**: Implemented raw `llama_tokenize` / `llama_decode` / `llama_sample` loop for granular control over the thinking process.

### 2. The Neuro-Link (IPC)
*   **Named Pipes**: Replaced lossy UDP sockets with Windows Named Pipes (`\\.\pipe\SYNZ_NeuroLink`) for reliable, high-speed communication between the C++ Brain and the Unity Body.
*   **System Prompt Injection**: Implemented a "Hypnosis" layer (System Prompts) to enforce the "Synza" personality (Sassy/Tsundere) at the context level.

### 3. Dual-Brain Architecture (Hybrid)
*   **Tier 1 (The Face)**: Defined a Custom SLM layer (PyTorch/Unsloth) for pure interaction and personality (Future Training Pipeline).
*   **Tier 2 (The Engineer)**: The current C++ Qwen implementation handles the heavy lifting of code analysis and logic.
*   **Hybrid Workflow**: Retained the Python environment as a Research & Training lab for fine-tuning GGUF models, while C++ handles the production runtime.

### 4. Codebase Restructuring
*   **Archiving**: Moved legacy Python/Watcher components to `_Archive/` and `TheBrain/` (Training Layer).
*   **Build System**: Created a portable `CMakeLists.txt` that automatically handles `llama.cpp` dependencies and GPU (CUDA/Metal) configuration.

## 🔜 Next Steps
*   Fine-tuning the "Face" SLM on interaction datasets.
*   Connecting the `NeuroLink` pipe to the Unity C# Overlay.
*   Replacing manual chat input with the `std::filesystem` Log Watcher.
