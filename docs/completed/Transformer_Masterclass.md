# 🧠 The Architect's Guide: Building a Transformer from Scratch

Welcome, Architect. You are about to build a brain.
We are not using `AutoModel`. We are using `torch.nn` and raw mathematics.

## The Goal
Build a file named `TheBrain/model.py`.
This file will contain the class `NanoSYNZ`, a decoder-only Transformer (like GPT-2).

---

## Part 1: The Heart (Self-Attention)

The core mechanism of a Transformer is "Self-Attention".
It allows tokens to "look at" other tokens to understand context.
*   **Query (Q)**: What am I looking for?
*   **Key (K)**: What do I contain?
*   **Value (V)**: What do I communicate?

### Step 1: Create the `Head`
A single "Head" of attention.

```python
import torch
import torch.nn as nn
from torch.nn import functional as F

class Head(nn.Module):
    """ one head of self-attention """

    def __init__(self, head_size, n_embed, block_size):
        super().__init__()
        self.key = nn.Linear(n_embed, head_size, bias=False)
        self.query = nn.Linear(n_embed, head_size, bias=False)
        self.value = nn.Linear(n_embed, head_size, bias=False)
        
        # 'tril' ensures we can't look into the future (Decoder-only property)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))

        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        B,T,C = x.shape # Batch, Time, Channels
        k = self.key(x)   # (B,T,hs)
        q = self.query(x) # (B,T,hs)
        
        # Compute Attention Scores ("Affinities")
        # (B, T, hs) @ (B, hs, T) -> (B, T, T)
        wei = q @ k.transpose(-2, -1) * k.shape[-1]**-0.5
        
        # Mask future tokens (The "Decoder" logic)
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1) # Normalize
        wei = self.dropout(wei)
        
        # Aggregation
        v = self.value(x) 
        out = wei @ v # (B, T, T) @ (B, T, hs) -> (B, T, hs)
        return out
```

---

## Part 2: The Multi-Head Attention

One head is smart. Multiple heads are smarter. They can look at different things (one looks at grammar, one looks at tone, etc.).

### Step 2: The `MultiHeadAttention` Module

```python
class MultiHeadAttention(nn.Module):
    """ multiple heads of self-attention in parallel """

    def __init__(self, num_heads, head_size, n_embed, block_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size, n_embed, block_size) for _ in range(num_heads)])
        self.proj = nn.Linear(head_size * num_heads, n_embed)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        # Run all heads in parallel
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.proj(out) # Project back to residual pathway
        out = self.dropout(out)
        return out
```

---

## Part 3: The Neuron (Feed Forward)

After "Thinking" (Attention), the brain needs to "Process" (Feed Forward Network).

### Step 3: The `FeedFoward` Layer

```python
class FeedFoward(nn.Module):
    """ a simple linear layer followed by a non-linearity """

    def __init__(self, n_embed):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embed, 4 * n_embed), # Expand dimension (4x is standard)
            nn.ReLU(),
            nn.Linear(4 * n_embed, n_embed), # Project back
            nn.Dropout(0.1),
        )

    def forward(self, x):
        return self.net(x)
```

---

## Part 4: The Block

Putting it together into a Transformer Block.

### Step 4: The `Block` Class

```python
class Block(nn.Module):
    """ Transformer block: communication followed by computation """

    def __init__(self, n_embed, n_head, block_size):
        super().__init__()
        head_size = n_embed // n_head
        self.sa = MultiHeadAttention(n_head, head_size, n_embed, block_size)
        self.ffwd = FeedFoward(n_embed)
        self.ln1 = nn.LayerNorm(n_embed)
        self.ln2 = nn.LayerNorm(n_embed)

    def forward(self, x):
        # Deviation from original paper: Pre-Norm architecture (better stability)
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x
```

---

## Part 5: The SYNZ Face (The Model)

Finally, the full GPT model.

### Step 5: `NanoSYNZ`

```python
class NanoSYNZ(nn.Module):

    def __init__(self, vocab_size, n_embed, block_size, n_head, n_layer):
        super().__init__()
        # each token directly reads off the logits for the next token from a lookup table
        self.token_embedding_table = nn.Embedding(vocab_size, n_embed)
        self.position_embedding_table = nn.Embedding(block_size, n_embed)
        self.blocks = nn.Sequential(*[
            Block(n_embed, n_head, block_size) for _ in range(n_layer)
        ])
        self.ln_f = nn.LayerNorm(n_embed) # final layer norm
        self.lm_head = nn.Linear(n_embed, vocab_size)
        self.block_size = block_size

    def forward(self, idx, targets=None):
        B, T = idx.shape

        # idx and targets are both (B,T) tensor of integers
        tok_emb = self.token_embedding_table(idx) # (B,T,C)
        pos_emb = self.position_embedding_table(torch.arange(T, device=idx.device)) # (T,C)
        x = tok_emb + pos_emb # (B,T,C)
        x = self.blocks(x) # (B,T,C)
        x = self.ln_f(x) # (B,T,C)
        logits = self.lm_head(x) # (B,T,vocab_size)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits, targets)

        return logits, loss

    def generate(self, idx, max_new_tokens):
        # idx is (B, T) array of indices in the current context
        for _ in range(max_new_tokens):
            # crop idx to the last block_size tokens
            idx_cond = idx[:, -self.block_size:]
            # get the predictions
            logits, loss = self(idx_cond)
            # focus only on the last time step
            logits = logits[:, -1, :] # becomes (B, C)
            # apply softmax to get probabilities
            probs = F.softmax(logits, dim=-1) # (B, C)
            # sample from the distribution
            idx_next = torch.multinomial(probs, num_samples=1) # (B, 1)
            # append sampled index to the running sequence
            idx = torch.cat((idx, idx_next), dim=1) # (B, T+1)
        return idx
```
