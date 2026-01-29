# SYNZ Deployment Plan 📦

This guide outlines how to package SYNZ into a distributable format (e.g., for a Hackathon Demo or Release) so users can run it without needing to install Unity or Python manually (if using embedded python) or just simplifying the run process.

> **Goal:** Create a `SYNZ_Release.zip` that works on any NVIDIA PC.

---

## Phase 1: The Body (Unity Build) 💃
We need to stop running Unity in the Editor and build a standalone EXE.

1.  **Open Unity** -> `File` -> `Build Settings`.
2.  **Add Open Scenes:** Ensure your main scene is checked.
3.  **Target Platform:** `Windows (x86_64)`.
4.  **Compression:** `LZ4` (Fast startup) or `LZ4HC`.
5.  **Build:**
    *   Create a folder inside your project called `Build`.
    *   Click Build.
    *   Name the exe: `SYNZ_Body.exe`.
6.  **Verify:** Run `Build/SYNZ_Body.exe` to make sure the anime girl appears and looks correct.

---

## Phase 2: The Brain (Python Logic) 🧠
We simply ship the `TheBrain` folder and `venv` (Virtual Environment).

*   **Note:** Shipping `venv` is risky if the user has a different path configuration, but since we used the `%~dp0` patch in `start_synz.bat`, it is remarkably portable as long as they unzip it.
*   **Alternative (Pro):** Use "Embeddable Python" to make it truly portable, but for a Hackathon, zipping the `venv` usually works if the target PC uses the same OS architecture (Windows x64).

---

## Phase 3: The Launcher (One Button) 🚀
We update `start_synz.bat` to launch the **Included Unity Build** instead of asking the user to press Play.

**Modified `start_synz.bat` Logic:**
```batch
@echo off
cd /d "%~dp0"
...
echo [3/4] Launching Brains...
start ...
start ...
start ...

echo [4/4] Launching Body...
start "" "Build\SYNZ_Body.exe"
```

**Optional Polish:**
Use **[Bat To Exe Converter](https://github.com/zhongyang219/Bat-To-Exe-Converter)** to turn this `.bat` into `SYNZ_Launcher.exe` with a custom icon.

---

## Phase 4: Final Folder Structure 📂
Organize your release folder like this:

```
SYNZ_Release/
├── Build/                  <-- The Unity Game
│   ├── SYNZ_Body.exe
│   └── UnityPlayer.dll
├── TheBrain/               <-- Your Python Code
│   ├── brain_server.py
│   └── (all other py files)
├── models/                 <-- The Llama-3 Model (Copy it here)
├── venv/                   <-- The Python Environment
├── start_synz.bat          <-- The Trigger
└── README.md
```

## Phase 5: Distribution 🚚
1.  **Zip It:** Right-click `SYNZ_Release` -> *Compress to ZIP*.
2.  **Test It:** Send the ZIP to another computer/friend.
    *   Unzip.
    *   Run `start_synz.bat`.
    *   If it works, you ship it!

---

## Checklist for Later
- [ ] Build Unity Project to `Build/`.
- [ ] Copy `models/*.gguf` to Release folder? (Or tell user to download it).
- [ ] Update `start_synz.bat` to point to `Build/SYNZ_Body.exe`.
- [ ] Test on a fresh PC.
