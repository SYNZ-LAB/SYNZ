# SYNZ: Hybrid Agent Implementation Plan

## Goal
Build a "Dual-Brain" Agentic Co-worker.
1.  **Left Brain** (Skill): C++ Native Core running Qwen 2.5 (1.5/7B). Handles Logic, Code, OS functionality.
2.  **Right Brain** (Personality): Python Custom Transformer (NanoSYNZ). Handles Personality, Chat, VTuber Control.

## User Review Required
> [!IMPORTANT]
> **Python 3.14 Compatibility**: The user is running bleeding-edge Python. We are training on CPU initially due to lack of stable CUDA support for 3.14.

## Proposed Architecture

### 1. SYNZ Core (C++)
*   **Role**: Host, Logic Engine, Sentinel.
*   **Status**: **ACTIVE**.
*   **Components**:
    *   `src/LlamaEngine.h`: Logically wraps `llama.cpp`.
    *   `src/CodeMonitor.h`: Recursively watches `.cs` files.
    *   `src/NeuroLink.h`: IPC with Unity.

### 2. SYNZ Face (Python)
*   **Role**: Personality, Chat, "The Soul".
*   **Status**: **IN CONSTRUCTION**.
*   **Components**:
    *   [NEW] `TheBrain/model.py`: `NanoSYNZ` (GPT-style Transformer built from scratch).
    *   [NEW] `TheBrain/train_scratch.py`: Manual training loop.
    *   [NEW] `TheBrain/personality_data.json`: Curated "Sassy Engineer" dataset.

### 3. The Bridge (Integration)
*   **Mechanism**: The C++ Core will launch the Python Face as a subprocess or talk via UDP.
*   **Protocol**:
    *   **Logic Request**: Core handles it locally.
    *   **Chat Request**: Core forwards to Face -> Face replies -> Core sends to Unity.

## Verification Plan

### Automated Tests
*   **Crash Test**: `AutoCrash.cs` triggers Core.
*   **Chat Test**: Send "Hello" to Core -> Core routes to Face -> Face replies "I'm busy."

### Manual Verification
*   User validates "Sassiness" of the new Face model after training.
