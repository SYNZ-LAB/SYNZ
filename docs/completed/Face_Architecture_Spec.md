# 🧠 SYNZ Face: Custom Transformer Specification

We are building a decoder-only Transformer (GPT-style) from scratch to serve as the "Personality Core".

## 1. Parameters (The "Small" Brain)
We want this to be fast and lightweight, running alongside the Main Brain.

*   **Vocab Size**: 4096 (Small custom vocabulary, specific to your way of speaking)
*   **Context Window**: 512 Tokens (Short term memory, enough for a quick reply)
*   **Embedding Dim**: 256 (Small vector space)
*   **Layers**: 6
*   **Heads**: 8
*   **Total Params**: ~5 Million (Tiny! But enough for a specific personality)

## 2. Architecture
```python
class NanoSYNZ(nn.Module):
    def __init__(self):
        self.token_embedding = nn.Embedding(VOCAB_SIZE, EMBED_DIM)
        self.position_embedding = nn.Embedding(CONTEXT_LEN, EMBED_DIM)
        self.blocks = nn.Sequential(*[
            TransformerBlock(EMBED_DIM, N_HEADS) for _ in range(N_LAYERS)
        ])
        self.ln_f = nn.LayerNorm(EMBED_DIM)
        self.head = nn.Linear(EMBED_DIM, VOCAB_SIZE)
```

## 3. Data Flow
1.  **Input**: "User says: The code crashed."
2.  **Tokenizer**: Breaks into IDs: `[User, says, :, The, code, crashed, .]`
3.  **Transformer**: Predicts next token.
4.  **Output**: "SYNZ says: *Sigh* What did you do?"

## 4. Files Required
1.  `TheBrain/model.py`: The Neural Network definition.
2.  `TheBrain/train_scratch.py`: The Training Loop.
3.  `TheBrain/tokenizer.py`: The text processor.
