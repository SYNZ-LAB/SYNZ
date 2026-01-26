# Clipboard to Brain Integration Guide 📋

This guide explains how to give SYNZ the ability to read your system clipboard.
This allows you to copy a block of code and simply say "Read this" instead of pasting it into a messy terminal line.

## 1. Prerequisites
We need a library to access the OS clipboard.

```bash
pip install pyperclip
```

## 2. Implementation Steps

### Step A: Import Library
Open `TheBrain/face_server.py`.
Add this to the top imports:

```python
import pyperclip
```

### Step B: Add the Trigger
Inside the main `while True:` loop, look for where we handle `!read` or `!write`.
Add a new check for `!clip` or specialized voice trigger logic.

```python
        # [NEW] Clipboard Tool
        # Triggered by typing "!clip" OR by voice command "Read clipboard"
        is_clipboard_request = user_msg.strip() == "!clip" or "read clipboard" in user_msg.lower()
        
        if is_clipboard_request:
             try:
                 content = pyperclip.paste()
                 if not content:
                     response = "[SYSTEM] Clipboard is empty."
                 else:
                     print(f"[THE BODY] grabbing {len(content)} chars from clipboard...")
                     
                     # We treat this as user input.
                     # "Here is the code from my clipboard: \n <content>"
                     user_msg = f"Analyzing clipboard content:\n{content}"
                     
                     # Allow it to flow down to the Core naturally
                     # It will hit the 'needs_search' or Core logic below.
             except Exception as e:
                 print(f"[ERR] Clipboard Error: {e}")
                 # Continue gracefully
```

## 3. Usage
1.  **Select & Copy** text in your browser or IDE.
2.  **Say:** "Read clipboard and fix the bug."
3.  **Result:** SYNZ reads the invisible text and responds.

## 4. Advanced (Optional)
If the clipboard content is HUGE (e.g. 500 lines), you might want to truncate it or warn the user before sending it to the LLM to save context window.

```python
if len(content) > 10000:
    print("[WARN] Clipboard too large! Truncating...")
    content = content[:10000] + "\n...(truncated)"
```
