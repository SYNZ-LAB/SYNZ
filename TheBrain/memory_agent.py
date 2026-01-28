import os
import uuid

# --- SAFETY WRAPPER ---
try:
    import chromadb
    from chromadb.utils import embedding_functions
    MEMORY_AVAILABLE = True
except ImportError:
    print("[MEMORY] WARN: ChromaDB/SentenceTransformers not found (Python 3.14?). Memory disabled.")
    MEMORY_AVAILABLE = False
except Exception as e:
    print(f"[MEMORY] WARN: Dependency Error: {e}")
    MEMORY_AVAILABLE = False


class MemoryAgent:
    def __init__(self, db_path="memory_db"):
        if not MEMORY_AVAILABLE:
            print("[MEMORY] Hippocampus OFFLINE (Dummy Mode).")
            return

        try:
            # Create DB directory if not exists (relative to this script)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            full_db_path = os.path.join(script_dir, db_path)
            
            print(f"[MEMORY] Initializing Hippocampus at {full_db_path}...")
            
            # 1. Setup Database (Persistent)
            self.client = chromadb.PersistentClient(path=full_db_path)
            
            # 2. Setup Embedding (The "Encoder")
            # "all-MiniLM-L6-v2" is small, fast, and good for English.
            self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            
            # 3. Get/Create Collection
            self.collection = self.client.get_or_create_collection(
                name="synz_memories",
                embedding_function=self.ef
            )
            print(f"[MEMORY] Hippocampus Loaded. {self.collection.count()} memories stored.")
        except Exception as e:
             print(f"[MEMORY] Failed to load DB: {e}. Switching to Dummy Mode.")
             self.collection = None

    def remember(self, text, metadata=None):
        """Saves a thought/conversation to the database."""
        if not MEMORY_AVAILABLE or not hasattr(self, 'collection') or self.collection is None:
            return

        try:
             # Random ID
             mem_id = str(uuid.uuid4())
             
             self.collection.add(
                 documents=[text],
                 metadatas=[metadata or {"source": "conversation", "timestamp": "now"}],
                 ids=[mem_id]
             )
        except Exception as e:
             print(f"[ERR] Memory Save Failed: {e}")

    def recall(self, query, n_results=2):
        """Finds relevant memories based on the query."""
        if not MEMORY_AVAILABLE or not hasattr(self, 'collection') or self.collection is None:
            return ""

        try:
            if self.collection.count() == 0:
                return ""

            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Extract text
            memories = results['documents'][0]
            if not memories:
                return ""
            
            # Format
            context = "### RECALLED MEMORIES ###\n"
            for mem in memories:
                context += f"- {mem}\n"
            return context
            
        except Exception as e:
            print(f"[ERR] Memory Recall Failed: {e}")
            return ""

if __name__ == "__main__":
    # Test
    m = MemoryAgent()
    m.remember("My name is User.")
    print(m.recall("What is my name?"))
