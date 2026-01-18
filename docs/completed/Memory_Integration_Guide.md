# Phase 11: Long-Term Memory (The Hippocampus)

Currently, SYNZ has "Amnesia". She forgets everything when you restart her.
We will fix this using **RAG (Retrieval Augmented Generation)**.

## 1. The Strategy
We perform "Brain Surgery" to add a persistent database.

1.  **Storage:** Use **ChromaDB** (a local Vector Database).
2.  **Encoding:** Use **Sentence-Transformers** (turns text into numbers/embeddings).
3.  **Recall:** precise "Semantic Search" (finding memories by *meaning*, not just keywords).

## 2. Prerequisites
You will need to install these Python libraries:

```bash
pip install chromadb sentence-transformers
```

## 3. The Memory Agent (`memory_agent.py`)
Create a new file `TheBrain/memory_agent.py`. This class handles the database.

```python
import chromadb
from chromadb.utils import embedding_functions
import os

class MemoryAgent:
    def __init__(self, db_path="memory_db"):
        # 1. Setup Database (Persistent)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 2. Setup Embedding (The "Encoder")
        # "all-MiniLM-L6-v2" is small, fast, and good for English.
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        # 3. Get/Create Collection
        self.collection = self.client.get_or_create_collection(
            name="synz_memories",
            embedding_function=self.ef
        )
        print(f"[MEMORY] Hippocampus Loaded. {self.collection.count()} memories stored.")

    def remember(self, text, metadata=None):
        """Saves a thought/conversation to the database."""
        try:
             # ID based on count (simple)
             mem_id = f"mem_{self.collection.count() + 1}"
             
             self.collection.add(
                 documents=[text],
                 metadatas=[metadata or {"source": "conversation"}],
                 ids=[mem_id]
             )
             print(f"[MEMORY] Saved: '{text[:30]}...'")
        except Exception as e:
             print(f"[ERR] Memory Save Failed: {e}")

    def recall(self, query, n_results=2):
        """Finds relevant memories based on the query."""
        try:
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
```

## 4. Integration (`face_server.py`)
We hook this into the main loop, just like the Search Agent.

### A. Initialization
```python
from memory_agent import MemoryAgent
# ...
brain = MemoryAgent()
```

### B. The Recall Loop (Injecting Memory)
Before asking Llama-3, check if we remember anything relevant.

```python
# ... inside main loop ...
memory_context = brain.recall(user_msg)
full_prompt = memory_context + "\n" + user_msg
# ... send to Core ...
```

### C. The Save Loop (Consolidating Memory)
After SYNZ speaks, save the interaction.
*Tip: Only save "important" things, or just save everything for now.*

```python
# ... after response ...
brain.remember(f"User: {user_msg}\nSYNZ: {response}")
```

## 5. Result
If you tell her: *"My name is Admin."*
She saves it.
Next week, if you ask *"What is my name?"*:
1.  She recalls: `"User: My name is Admin."`
2.  She answers: *"Your name is Admin! ❤️"*
