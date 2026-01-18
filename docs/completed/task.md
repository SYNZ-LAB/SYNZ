# Tasks

- [x] Analyze current project state <!-- id: 0 -->
- [x] Implement Sentinel (Legacy Win32 Version) <!-- id: 4 -->
- [ ] **Migrate to Native Embedded Architecture** <!-- id: 10 -->
    - [x] Create CMakeLists.txt (Teaching Mode) <!-- id: 11 -->
    - [x] Download Qwen Model <!-- id: 15 -->
    - [x] Build SYNZ Core (CPU Mode) <!-- id: 16 -->
    - [x] Implement C++ Inference Wrapper (LlamaContext) <!-- id: 12 -->
    - [x] Implement Log Watcher (std::filesystem polling) <!-- id: 13 -->
    - [x] Create Integrated main.cpp <!-- id: 14 -->
    - [x] **Implement Unity Named Pipe Client** (C#) <!-- id: 17 -->
        - [x] Create NeuroLinkClient.cs
        - [x] Verify Connection
        - [x] Verify End-to-End Reaction (Trigger Error)
    - [/] **Implement Code Sentinel** (Grammarly for Code)
        - [x] Create `CodeMonitor` class (header-based)
        - [x] Integrate into `main.cpp` loop
        - [x] Verify Real-time Code Analysis

- [ ] **Phase 4: Constructing The Face (Python)** <!-- id: 20 -->
    - [x] **Architecture Design** <!-- id: 21 -->
        - [x] Define `NanoSYNZ` Class (PyTorch)
        - [x] Implement Multi-Head Attention manually
    - [x] **Data Pipeline** <!-- id: 22 -->
        - [x] Train Custom Tokenizer (BPE)
        - [x] Parse `personality_data.json`
    - [/] **Training Loop** <!-- id: 23 -->
        - [x] Write `train_scratch.py`
        - [x] Monitor Loss until it "Speaks"
    - [/] **Reinforcement Loop (RL-Lite)** <!-- id: 24 -->
        - [x] Add `feedback` endpoint to `face_server.py`
        - [x] Auto-append "Good" interactions to `training_data.txt`
    - [ ] Convert to GGUF & Integrate with C++ Core <!-- id: 25 -->

- [ ] **Phase 5: The Body (Live2D Cubism SDK)** <!-- id: 30 -->
    - [ ] **SDK Setup** <!-- id: 31 -->
        - [ ] Download & Import Cubism SDK (User Action)
        - [ ] Import `.moc3` Model
    - [ ] **Native Controller** <!-- id: 32 -->
        - [ ] Create `CubismSYNZController.cs`
        - [ ] Implement `UpdateParameters()` (Eye Open, Mouth Open)
        - [ ] Map `<TAGS>` to Expression Parameters

- [/] **Phase 6: The Voice (TTS)** <!-- id: 40 -->
    - [x] Install `edge-tts`, `soundfile`
    - [x] Create `tts_engine.py` prototype
    - [x] Integrate generation into `face_server.py`
    - [x] Implement Audio Stream (File Path Signal via UDP)

- [/] **Phase 7: The Senses (Audio Integration)** <!-- id: 50 -->
    - [x] **Unity Earcup** (FaceBridge.cs)
    - [x] **Unity Mouth** (SimpleAudioPlayer.cs)
    - [ ] **Verify Audio Playback**
    - [ ] **Implement Lip Sync** (Volume or OVRLipSync)
    - [/] **Implement Speech-to-Text** (The Ears)

- [ ] **Phase 8: Connecting the Brain (C++ Core Integration)** <!-- id: 60 -->
    - [x] Create `Knowledge_Core_Guide.md`
    - [x] **Download Qwen Model** (Confirmed Installed)
    - [x] **Compile SYNZ Core** (Release Mode)
    - [x] **Run Dual-Process Stack** (Python Voice + C++ Logic)
    - [x] **Verify Logic Queries** (e.g. "Write me code")

