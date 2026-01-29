# SYNZ: Full System Verification Guide 🧪

This guide explains how to test the **Entire Loop** (Brain + Ears + Face + Unity Body).

---

## Phase 1: The Awakening (Launch) 🚀

1.  **Start the Brains:**
    *   Go to your project folder.
    *   Double-click `start_synz.bat`.
    *   **Verify:** You should see **3 Black Terminal Windows** open.
        *   *Window 1 (Brain):* Wait until it says `[BRAIN] Model Online`.
        *   *Window 2 (Face):* Wait until it says `[THE SELF] Personality Loaded`.
        *   *Window 3 (Ears):* It should show a volume meter `[      ]`.

2.  **Start the Body:**
    *   Open your Unity Project.
    *   Open the scene with your Live2D Model.
    *   Press the **Play Button** (▶) at the top.
    *   **Verify:**
        *   Look at the **Console** tab in Unity.
        *   You MUST see: `<color=green>[NeuroLink] UDP Socket created...</color>`
        *   If you see "Connection Failed", something is wrong (check `start_synz.bat` is running).

---

## Phase 2: The "Handshake" 🤝

Now that both are running, they need to find each other.

1.  **Check the Face Window (Python Terminal):**
    *   It should say: `[SYSTEM] Body Connected at ('127.0.0.1', xxxx)`
    *   This means Python sees Unity.

2.  **Check the Unity Console:**
    *   It sends "Unity Connected" every few seconds.
    *   This keeps the connection alive.

---

## Phase 3: The Interaction Test 🗣️

1.  **Wake Her Up:**
    *   Say clearly: **"SYNZ!"**
    *   *Check the Ears Window:* It should print `[WAKE] Waking up!`.

2.  **Speak a Command:**
    *   Say: **"Hello, can you see me?"**
    *   *Check the Face Window:* It should print `[USER SAYS]: Hello...`
    *   *Check the Brain Window:* It should say `[REQ] Thinking...`

3.  **The Response (The Moment of Truth):**
    *   **Text:** Python prints her reply (e.g., "Yes, I see you.").
    *   **Audio:** Python generates `response.mp3`.
    *   **Action:**
        *   Unity Console should log: `[SYNZ]: Yes, I see you. (NORMAL)`
        *   **HEAR:** You should hear her voice through your speakers.
        *   **SEE:** Her mouth should move (Lip Sync) and her face should express emotions (Blush/Eyes).

---

## ❌ Troubleshooting Checklist

**"I don't hear anything!"**
*   Is Unity Volume UP? (Check the "Mute Audio" button in Game View).
*   Did Python say `[TTS] Saved to response.mp3`?
*   Did Unity receive `[AUDIO]` packet? (Check Console).

**"Her mouth isn't moving!"**
*   Does your Live2D Model have `ParamMouthOpenY`?
*   Select the Model in via Hierarchy while playing. Look at `SYNZLive2DController` script in Inspector. Is `Sensitivity` > 0?

**"She ignores me!"**
*   Check your Mic settings in Windows.
*   Look at the "Ears" window. Do the bars `[||||  ]` move when you talk?
