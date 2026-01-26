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

- [ ] **Phase 12: The Eyes (Vision)** <!-- id: 100 -->
    - [ ] **VLM Integration** <!-- id: 101 -->
        - [ ] Install `transformers` `pillow` `mss`
        - [ ] Create `vision_server.py` (Moondream2 / Llava)
    - [ ] **Sight Loop** <!-- id: 102 -->
        - [ ] Implement Screenshot mechanism
        - [ ] Implement "Describe Screen" trigger

- [ ] **Phase 14: Agency (Humanization)** <!-- id: 120 -->
    - [ ] **Emotional Core** <!-- id: 121 -->
        - [ ] Create `mood.json` (Happiness/Energy)
        - [ ] Implement Decay/Boost Logic
    - [ ] **Proactive Loop** <!-- id: 122 -->
        - [ ] Monitor Silence Duration
        - [ ] Trigger Self-Initiated Chat

- [ ] **Phase 13: The Body (VTuber / VRM)** <!-- id: 30 -->
    - [ ] **SDK Setup** <!-- id: 31 -->
        - [ ] Download & Import UniVRM Package (User Action)
        - [ ] Import `.vrm` Model
    - [ ] **Animation Controller** <!-- id: 32 -->
        - [ ] Create `ExpressionController.cs`
        - [ ] Implement Lip Sync (OVRLipSync or Audio Amplitude)
        - [ ] Map Network Signals (`[SASS]`) to Blendshapes

- [ ] **Phase 15: The Hands (Agentic Coding)** <!-- id: 130 -->
    - [ ] **Editor Agent** <!-- id: 131 -->
        - [ ] Create `editor_agent.py` (Safe File I/O)
        - [ ] Implement Backup/Rollback Logic
    - [ ] **Integration** <!-- id: 132 -->
        - [ ] Enable `!edit` command in `face_server.py`

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
    - [x] **Hardware Acceleration** <!-- id: 71 -->
        - [x] Verify CUDA Toolkit (nvcc)
        - [x] Reconfigure CMake with `-DGGML_CUDA=ON`
        - [x] Recompile SYNZ Core (GPU Mode)
    - [x] **Brain Transplant** <!-- id: 72 -->
        - [x] Download `Llama-3.1-8B-Instruct.gguf`
        - [x] Update `main.cpp` to load new model
    - [ ] **Verify Superintelligence** (Benchmark Speed/Smartness)

- [x] **Phase 10: Sensorial Expansion (The Internet)** <!-- id: 80 -->
    - [x] **Search Agent** <!-- id: 81 -->
        - [x] Install `duckduckgo-search`
        - [x] Create `search_agent.py`
    - [x] **Logic Bridge** <!-- id: 82 -->
        - [x] Integrate Search into `face_server.py`
        - [x] Test Real-time Information Retrieval (e.g. "Bitcoin Price")

- [x] **Phase 11: Long-Term Memory (RAG)** <!-- id: 90 -->
    - [x] **Vector Database** <!-- id: 91 -->
        - [x] Install `chromadb` & `sentence-transformers`
        - [x] Create `memory_agent.py`
    - [x] **Memory Loop** <!-- id: 92 -->
        - [x] Integrate Recall (Before Generation)
        - [x] Integrate Consolidation (After Generation)

