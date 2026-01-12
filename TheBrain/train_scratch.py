# 🏋️‍♀️ SYNZ Trainer (Manual Implementation)
import torch
import torch.nn as nn
from torch.nn import functional as F
from model import NanoSYNZ
import json
import os

# --- Configuration ---
batch_size = 32 # Contexts processed in parallel
block_size = 64 # REDUCED for small dataset (was 256)
max_iters = 5000
eval_interval = 500
learning_rate = 3e-4
device = 'cuda' if torch.cuda.is_available() else 'cpu'
eval_iters = 200
n_embed = 384
n_head = 6
n_layer = 6
dropout = 0.2

print(f"[SYNZ] Training on: {device}")

# --- 1. Load Data ---
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "personality_data.json")

try:
    with open(data_path, 'r', encoding='utf-8') as f:
        # Load JSON and extract text
        raw_data = json.load(f)
        # Combine all "text" fields into one giant string
        # Assuming format: [{"text": "Hello"}, {"text": "World"}]
        text = "\n".join([item["text"] for item in raw_data])
except FileNotFoundError:
    print("[ERROR] personality_data.json not found! Using dummy text.")
    text = "Hello SYNZ. I am your Architect. " * 1000

print(f"[SYNZ] Data Loaded. Length: {len(text)} characters")

# --- 2. Tokenizer (Character Level) ---
# Create mapping from unique characters to integers
chars = sorted(list(set(text)))
vocab_size = len(chars)
print(f"[SYNZ] Vocabulary Size: {vocab_size} | Chars: {''.join(chars)}")

stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }
encode = lambda s: [stoi[c] for c in s] # Encoder: take a string, output a list of integers
decode = lambda l: ''.join([itos[i] for i in l]) # Decoder: take a list of integers, output a string

# Train/Test Split
data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9 * len(data)) # first 90% will be train, rest val
train_data = data[:n]
val_data = data[n:]

# --- 3. Batch Loader ---
def get_batch(split):
    # generate a small batch of data of inputs x and targets y
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    x, y = x.to(device), y.to(device)
    return x, y

# --- 4. Initialize Brain ---
model = NanoSYNZ(
    vocab_size=vocab_size, 
    n_embed=n_embed, 
    block_size=block_size, 
    n_head=n_head, 
    n_layer=n_layer
)
m = model.to(device)
print(f"[SYNZ] Model Parameters: {sum(p.numel() for p in m.parameters())/1e6:.2f} M")

# --- 5. Optimizer ---
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

# --- 6. Helper: Estimate Loss ---
@torch.no_grad()
def estimate_loss():
    out = {}
    model.eval()
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out

# --- 7. Training Loop ---
print("[SYNZ] Starting Hypnosis Session (Training)...")

for iter in range(max_iters):

    # Every once in a while evaluate the loss on train and val sets
    if iter % eval_interval == 0 or iter == max_iters - 1:
        losses = estimate_loss()
        print(f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")

    # Sample a batch of data
    xb, yb = get_batch('train')

    # Evaluate the loss
    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

# --- 8. Save & Test ---
print("[SYNZ] Training Complete!")
torch.save(model.state_dict(), os.path.join(script_dir, "synz_face.pth"))
print("[SYNZ] Brain Saved to synz_face.pth")

# Generate a sample
context = torch.zeros((1, 1), dtype=torch.long, device=device)
print("\n[SYNZ SAYS]:")
print(decode(m.generate(context, max_new_tokens=100)[0].tolist()))
