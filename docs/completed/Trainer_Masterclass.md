# 🏋️‍♀️ The Trainer's Guide: Teaching the Brain

Welcome back, Architect.
You have a Brain (`model.py`), but it is empty. It knows nothing.
Now we must build the **Gym** (`train_scratch.py`).

## The Concept

Training a Language Model is simple:
1.  **Input**: "Hello, how are"
2.  **Target**: "ello, how are you" (shifted by 1)
3.  **Loss**: Did the model guess 'y' correctly? If not, adjust weights.

## Part 1: The Tokenizer (The Ear)
Computers don't speak English. They speak Numbers.
We need a way to turn "Hello" into `[8, 5, 12, 12, 15]`.
For this Nano model, we will use a **Character Tokenizer**. It's simple and effective for small datasets.

```python
# Create a mapping from Character to Integer
chars = sorted(list(set(text)))
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }
encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])
```

## Part 2: The Batcher (The Spoon)
We can't feed the whole Wikipedia at once. We feed it in "Batches".
*   `block_size`: How much context it sees (e.g., 256 chars).
*   `batch_size`: How many parallel streams (e.g., 64).

```python
def get_batch(split):
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    return x, y
```

## Part 3: The Optimizer (The Coach)
We use **AdamW**. It's the standard optimizer for Transformers.
It calculates "Gradients" (which direction to move the weights to reduce error) and updates the model.

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
```

## Part 4: The Loop (The Workout)
We run this thousands of times.

```python
for iter in range(max_iters):
    # 1. Get Data
    xb, yb = get_batch('train')
    
    # 2. Forward Pass (Think)
    logits, loss = model(xb, yb)
    
    # 3. Backward Pass (Learn)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
    
    print(f"step {iter}: loss {loss.item()}")
```

## Part 5: Saving (The Checkpoint)
After training, we save the weights so we can stick it into the C++ Application later.

```python
torch.save(model.state_dict(), "synz_face.pth")
```
