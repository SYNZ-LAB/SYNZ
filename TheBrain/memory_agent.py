import os
import json
import uuid
import time
from collections import Counter

# --- SAFETY WRAPPER ---
# We try to import ChromaDB, but since we know it fails on 3.14, we prioritize the JSON fallback logic
# if the import fails.

class MemoryAgent:
    def __init__(self, db_path="synz_memories.json"):
        # Path resolution
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_path = os.path.join(script_dir, db_path)
        self.mode = "JSON" # Force JSON mode for safety on this user's machine
        
        # Load existing
        self.memories = []
        self.load_memories()

        print(f"[MEMORY] Hippocampus Loaded (JSON Mode). {len(self.memories)} memories stored.")

    def load_memories(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
            except Exception as e:
                print(f"[MEMORY] Corrupt DB: {e}. Starting fresh.")
                self.memories = []

    def save_memories(self):
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, indent=2)
        except Exception as e:
            print(f"[ERR] Failed to save memory: {e}")

    def remember(self, text, metadata=None):
        """Saves a thought to JSON."""
        entry = {
            "id": str(uuid.uuid4()),
            "text": text,
            "metadata": metadata or {"source": "conversation", "timestamp": time.time()}
        }
        self.memories.append(entry)
        self.save_memories()

    def recall(self, query, n_results=2):
        """Finds memories using Keyword Matches (dumb but fast)."""
        if not self.memories:
            return ""

        # 1. Simple Keyword Scoring
        query_words = set(query.lower().split())
        scored = []
        
        for mem in self.memories:
            mem_text = mem['text']
            mem_words = set(mem_text.lower().split())
            
            # Intersection count
            overlap = len(query_words.intersection(mem_words))
            if overlap > 0:
                scored.append((overlap, mem_text))
        
        # 2. Sort by overlap
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # 3. Take top N
        top_memories = [x[1] for x in scored[:n_results]]
        
        if not top_memories:
            return ""

        # Format
        context = "### RECALLED MEMORIES (JSON) ###\n"
        for m in top_memories:
            context += f"- {m}\n"
        return context

if __name__ == "__main__":
    m = MemoryAgent()
    m.remember("My name is User.")
    m.remember("The sky is blue.")
    print(m.recall("What is my name?"))
