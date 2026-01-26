import os
import shutil
import time

class EditorAgent:
    def __init__(self, root_dir="."):
        # Restrict access to this folder and subfolders
        self.root_dir = os.path.abspath(root_dir)
        print(f"[HANDS] Editor initialized. Root: {self.root_dir}")

    def _is_safe(self, path):
        """Ensures path is within root_dir to prevent accessing system files."""
        try:
            # Handle relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.root_dir, path)
            
            abs_path = os.path.abspath(path)
            return abs_path.startswith(self.root_dir), abs_path
        except Exception as e:
            return False, str(e)

    def read_file(self, path):
        """Reads a file safely."""
        safe, abs_path = self._is_safe(path)
        if not safe:
            return f"[ERR] Access Denied: {path} is outside the sandbox."

        if not os.path.exists(abs_path):
            return f"[ERR] File not found: {path}"

        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"[ERR] Read Failed: {e}"

    def write_file(self, path, content):
        """Writes a file safely with backup."""
        safe, abs_path = self._is_safe(path)
        if not safe:
            return f"[ERR] Access Denied: {path} is outside the sandbox."

        try:
            # 1. Automatic Backup if file exists
            if os.path.exists(abs_path):
                timestamp = int(time.time())
                backup_path = f"{abs_path}.{timestamp}.bak"
                shutil.copy2(abs_path, backup_path)
                backup_msg = f"(Backup saved to {os.path.basename(backup_path)})"
            else:
                backup_msg = "(New file created)"

            # 2. Write
            # Ensure dir exists
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return f"[SUCCESS] Wrote {len(content)} bytes to {os.path.basename(path)}. {backup_msg}"
        except Exception as e:
            return f"[ERR] Write Failed: {e}"

if __name__ == "__main__":
    # Test
    hands = EditorAgent(".")
    print(hands.write_file("test_hands.txt", "Hello World!"))
    print(hands.read_file("test_hands.txt"))
