# Project Lilith: Prototype Roadmap 🚀

This document outlines high-impact features to transform Lilith from a log-monitor into a true Agentic Co-worker.

## 1. The Brain (Intelligence & Memory)
- [ ] **Short-Term Memory**: Implement a sliding window buffer so Lilith remembers the last 5 errors. If the same error happens 3 times, her personality should shift to "Frustrated" or "Concerned."
- [ ] **Code Context Injection**: When an error occurs, have The Watcher send the 10 lines of code surrounding the error. The Brain can then "reason" about the specific variable that is null.
- [ ] **Local TTS (Voice)**: Integrate a lightweight Text-to-Speech engine (like **Piper** or **Sherpa-ONNX**) so Lilith can actually speak her reactions.

## 2. The Body (VTuber Presence)
- [ ] **Dynamic Eye Tracking**: Make Lilith's eyes follow the user's mouse cursor or look towards the "Console" window when an error pops up.
- [ ] **Thinking State**: Add a "Processing" animation (e.g., a holographic glow or a specific Live2D motion) while the SLM is running inference.
- [ ] **Overlay Chat Bubble**: A sleek, glassmorphism-style UI bubble that appears next to the VTuber model showing her "inner thoughts" or the error summary.

## 3. The Watcher (Deep Integration)
- [ ] **Performance Monitoring**: Watch for FPS drops or high VRAM usage. Lilith could comment: *"Hey, the GPU is sweating... maybe check that infinite loop?"*
- [ ] **Git Integration**: Monitor git commits. If a build fails, Lilith can identify who "broke" it based on the last commit.

## 4. Agentic Actions (The "Co-worker" part)
- [ ] **Auto-Open Script**: If a `NullReferenceException` has a file path, Lilith sends a command to the Body to open that file in VS Code at the exact line number.
- [ ] **Documentation Lookup**: Automatically search local Unity/Unreal docs for the error code and provide a "Lilith-style" summary.

## 5. Aesthetic & UX Polish (The "Wow" Factor)
- [ ] **Glassmorphism UI**: Use blurred backgrounds and subtle gradients for the overlay windows to give it a modern, premium feel.
- [ ] **Mood-Reactive Lighting**: Change the "rim light" or "glow" of the VTuber model based on her current emotion (e.g., a soft red glow when frustrated, a bright cyan glow when thinking).
- [ ] **Micro-Animations**: Add subtle "breathing" or "floating" animations to the UI elements so the interface feels alive even when idle.
- [ ] **Particle Effects**: Trigger small "glitch" particles when a critical error occurs, or "sparkles" when a build finally succeeds.

---

### 💡 Quick Prototype Hack: "The Frustration Meter"
Add a `frustration` variable to `personality.py`. Every time an error is received within 60 seconds of the last one, increment it. Use this to scale the "Intensity" of the animations sent to Unity.
