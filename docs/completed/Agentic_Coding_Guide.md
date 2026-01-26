# Phase 15: The Hands (Agentic Coding)

Currently, SYNZ can only *talk* about code. This phase gives her the power to *touch* it.
This transforms her from a Consultant to a **Co-Worker**.

## 1. The Concept
We create an `EditorAgent` that acts as a safe interface to the filesystem.
It must be **Safe** (no deleting `C:\Windows`) and **reversible**.

## 2. Architecture (`editor_agent.py`)

### A. The Safety Layer
Before any write operation:
1.  **Whitelist Check:** Only allow edits in `C:\Projects\SYNZ` (or configured paths).
2.  **Backup:** Automatically copy the target file to `.bak` before writing.

### B. The Toolset
The Agent will support these tool calls from the LLM:
1.  `read_file(path)`
2.  `write_file(path, content)`
3.  `replace_block(path, search_text, replacement)` (For surgical edits)

## 3. Implementation Draft

Create `TheBrain/editor_agent.py`:

```python
import os
import shutil

class EditorAgent:
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)

    def _is_safe(self, path):
        """Ensures path is within root_dir."""
        abs_path = os.path.abspath(path)
        return abs_path.startswith(self.root_dir)

    def read_file(self, path):
        if not self._is_safe(path): return "[ERR] Access Denied"
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[ERR] {e}"

    def write_file(self, path, content):
        if not self._is_safe(path): return "[ERR] Access Denied"
        
        # 1. Backup
        if os.path.exists(path):
            shutil.copy(path, path + ".bak")
            
        # 2. Write
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"[SUCCESS] Wrote to {path} (Backup created)"
        except Exception as e:
             return f"[ERR] {e}"
```

## 4. Integration
In `face_server.py`:
1.  Initialize `hands = EditorAgent(".")`.
2.  Add a Trigger: "Edit [filename]" or "Fix this file".
3.  When triggered, pass the command to `hands`.

## 5. Security Warning ⚠️
**NEVER** give this agent access to your entire drive. Always restrict `root_dir`.
