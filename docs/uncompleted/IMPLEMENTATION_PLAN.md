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

## 🧪 Verification
- Start Server & Unity.
- Type "Sing for me".
- Verify:
    1. Audio generates in Python.
    2. Unity receives signal.
    3. Avatar plays audio.
    4. Mouth moves.

## ⚠️ Risks
- **Latency**: File IO might introduce ~500ms delay.
- **Locking**: Unity might try to read the file while Python is writing it. (Solution: Use temp names or standard handshake).
