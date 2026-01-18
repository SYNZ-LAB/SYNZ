# SYNZ Phase 7: The Voice of Unity (Audio Integration)

## 🎯 Objective
Connect the generated `response.mp3` or raw audio bytes from **face_server.py** to **Unity**, enabling the avatar to speak and sync lips to the audio.

## 🏗️ Architecture
- **Source**: `face_server.py` generates audio (Edge-TTS).
- **Transport**:
    - *Option A (File Watcher)*: Unity watches for changes to `response.mp3` and plays it. (Easiest)
    - *Option B (UDP Stream)*: Python sends audio bytes via UDP to Unity. (Fastest/Real-time)
- **Receiver**: `NeuroLinkClient.cs` in Unity.
- **Visuals**: `OVRLipSync` or simple volume-based jaw movement.

## 📋 Steps

### 1. Python Side (Audio Stream)
- [ ] Research: Best format to send to Unity (WAV bytes vs File Path).
- [ ] Implement `send_audio_signal(filepath)` in `face_server.py`.
- [ ] Send custom packet header `[AUDIO]` to Unity via UDP.

### 2. Unity Side (The Ear)
- [ ] Update `NeuroLinkClient.cs` to listen for `[AUDIO]` packets.
- [ ] Implement `AudioLoader`: Coroutine to load `.mp3/.wav` from disk or memory.
- [ ] Auto-play audio upon receipt.

### 3. Lip Sync (The Mouth)
- [ ] Add `AudioSource` component to Avatar.
- [ ] Script a simple "Talk Animation" (Toggle `IsTalking` bool while audio plays).
- [ ] (Advanced) Analyze spectrum data to drive Blendshapes (A, E, I, O, U).

### 4. The Ear (Speech-to-Text) [NEW]
- [ ] **Unity**: Capture Microphone input.
- [ ] **Unity**: Stream raw PCM audio to Python (Port 8007?).
- [ ] **Python**: Implement `stt_engine.py` (using `faster-whisper` or `speech_recognition`).
- [ ] **Python**: Transcribe Audio -> Inject into `face_server.py` as user text.

## 🧪 Verification
- Start Server & Unity.
- Speak "Hello".
- Verify: Unity sends audio -> Python transcribes "Hello" -> Brain replies.
- Type "Sing for me".
- Verify:
    1. Audio generates in Python.
    2. Unity receives signal.
    3. Avatar plays audio.
    4. Mouth moves.

## ⚠️ Risks
- **Locking**: Unity might try to read the file while Python is writing it. (Solution: Use temp names or standard handshake).

# SYNZ Phase 8: Awakening the Logic Core (C++ Integration)

## 🎯 Objective
Compile and run the `synz_core` executable to handle logic/code questions, while maintaining the Python Face for personality and voice.

## 📋 Steps

### 1. Model Setup
- [x] Verify `Qwen2.5-Coder-1.5B-Instruct-GGUF.gguf` is in `models/`.

### 2. Compilation (Build System)
- [ ] Run `cmake --build . --config Release` to generate `synz_core.exe`.

### 3. Dual-Process Launch
- [ ] Terminal A: Run `synz_core.exe` (Port 8006).
- [ ] Terminal B: Run `face_server.py` (Port 8005).

### 4. Verification
- Type: "Write a python script to count to 10".
- Flow: `Face` -> (UDP) -> `Core` -> (UDP) -> `Face` -> `User`.

