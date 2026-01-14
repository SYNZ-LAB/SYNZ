# Project SYNZ: Prototype Roadmap 🚀

This document outlines high-impact features to transform Lilith from a log-monitor into a true **Native Agentic Co-worker**.

## 1. The Brain (Native Intelligence)
- [ ] **Direct Memory Access**: Instead of UDP sockets, The Sentinel passes pointers to log strings directly to the Llama Context. Latency: < 1ms.
- [ ] **Quantized Experts**: Use low-bit quantization (Q4_K_M) to run "Gemini-Level" models (7B+) on consumer hardware (8GB VRAM).
- [ ] **Grammar Sampling**: Use `llama.cpp` grammars to force the AI to output *only* valid JSON or C# code patches.

## 2. The Body (Unity Integration)
- [ ] **Shared Memory IPC**: Use Windows Shared Memory to update Unity texture data / parameters instantly from the C++ core.
- [ ] **Bone Injection**: Control the VTuber's head/eye rotation directly from C++ output values (0-1).

## 3. The Sentinel (Filesystem Polling)
- [ ] **Debounced Polling**: Use `std::filesystem::last_write_time` with a 10ms debounce to catch "burst" writes from Unity correctly.
- [ ] **Smart Diffs**: Only send the *semantics* of the error (e.g., skip timestamps) to save context tokens.

## 4. Agentic Actions
- [ ] **Auto-Browser**: Integrate `embedded-chromium` or similar to let the C++ agent look up API docs and parse the HTML directly.
- [ ] **Git Blame**: Use `libgit2` (C++ git library) to check who broke the build natively.
