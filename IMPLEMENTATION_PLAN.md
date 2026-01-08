# Project Lilith: Implementation Plan

## 1. Current State Analysis

### ✅ What Works Now
- **Inference Pipeline**: `inference_server.py` can receive UDP packets, run them through the model, and send actions to Unity.
- **Tokenizer**: Can handle C#/C++ code and special `<ACTION_>` tokens.
- **VTS Integration**: Unity can talk to VTube Studio to trigger expressions.
- **Overlay Tech**: The Unity window correctly handles transparency and "Always on Top" via Win32 API.

### ❌ What Doesn't Work (Yet)
- **Personality Intelligence**: The model ignores `[PERSONALITY:TAGS]` because it hasn't been trained on them.
- **Memory**: Lilith "forgets" an error the moment she processes it.
- **Context**: The Watcher only sees the error line, not the code that caused it.

---

## 2. Order of Importance (Strategy)

1. **Intelligence (High)**: If the AI isn't smart/reactive, the VTuber is just a static overlay.
2. **Personality (High)**: This is the unique selling point (USP) of Project Lilith.
3. **Context (Medium)**: Necessary for "Agentic" behavior (fixing code).
4. **Aesthetics (Medium)**: Crucial for the "Premium" feel, but comes after logic.

---

## 3. Implementation Order (Step-by-Step)

### Phase 1: The "Smart" Brain (Priority #1)
- **Task**: Update `TheBrain/data/training_data.txt` with personality-tagged examples.
- **Task**: Implement `PersonalityManager.process_input` to handle the time-based frustration logic.
- **Task**: Retrain the model.

### Phase 2: The "Aware" Watcher (Priority #2)
- **Task**: Modify `TheWatcher/main.cpp` to use a buffer (e.g., `std::deque`) to store the last 5 lines of the log.
- **Task**: Update the UDP payload to include this context.

### Phase 3: The "Reactive" Body (Priority #3)
- **Task**: Implement `UpdateUIMood` in `LilithOverlay.cs`.
- **Task**: Create a simple "Thinking" UI element in Unity that activates when the Brain is processing.

---

## 4. First Step: Personality Training Clues
To start Phase 1, you need to modify your training data. 
**Clue**: Look at how `[PERSONALITY:TSUNDERE]` and `[PERSONALITY:HELPFUL]` can lead to different `<ACTION_>` tokens for the **exact same error**.
