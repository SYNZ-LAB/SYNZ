# Project SYNZ: Master Status & Roadmap 🚀

This document tracks the progress of **SYNZ Core**, a high-performance, local-first Native C++ Agentic Co-worker.

## 🧠 The Dual-Brain Architecture
**Concept:** Two specialized models running in tandem.
1.  **The Face (SLM)**: Custom-trained Small Language Model (PyTorch/GGUF). Handles personality, chatting, and "Vibe".
2.  **The Engineer (LLM)**: Qwen 2.5-Coder (GGUF). Handles logic, code fixes, and error analysis.

## 🟢 Completed Features

##  The Research & Training Layer (Python)
- [ ] **Personality Trainer**: Use `Unsloth` (Python) to fine-tune the GGUF models used by the C++ Core.
- [ ] **Data Processing**: Python scripts to scrape documentation and format it for the C++ RAG system.
- [x] **Prototype Brain**: The original PyTorch implementation (kept for reference/testing).

---

## 🟡 In Progress: The Native Pivot (SYNZ Core)

### 🏗️ Architecture (The Monolith)
- [ ] **Build System**: `CMakeLists.txt` with `FetchContent` for `llama.cpp`.
- [ ] **The Core**: `src/main.cpp` integrating Watcher + Inference in a single threads.

### 🧠 The Brain (Native Inference)
- [ ] **Llama.cpp Integration**:
    - [ ] `LlamaEngine` class wrapping `llama_model` and `llama_context`.
    - [ ] GPU Offloading (CUDA/Metal) configuration.
- [ ] **Expert Model**: Support for ~1.5B - 7B quantized models (e.g., DeepSeek-Coder-V2-Lite).

### 👁️ The Sentinel (Native Watcher)
- [ ] **Filesystem Polling**: `std::filesystem::last_write_time` based watcher.
- [ ] **Direct Memory Handshake**: Pass string pointers directly to `llama_decode` (Zero Latency).

---

## 🔮 Future Backlog

### 💃 The Body (Unity Integration)
- [ ] **Named Pipe / Shared Memory**: Replace UDP with high-speed IPC for Unity communication.
- [ ] **Neuro-sama Style**: Deep integration where C++ controls 3D bone rotations directly.

### 🧠 Advanced Intelligence
- [ ] **Personality LoRA**: Fine-tune a custom adapter (`synz-sassy.gguf`) on a dataset of 1000+ sarcastic coding reviews.
- [ ] **Memory Vector DB**: Integrate `usearch` for long-term memory of past user errors.

### 🛠️ Agentic Capabilities
- [ ] **Auto-Fix**: Brain generates a `git apply` compatible patch for simple bugs.
- [ ] **Docs RAG**: Vector database (using `usearch` C++ lib) for Unity documentation.
