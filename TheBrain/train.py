import os
import time
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from model import LilithConfig, LilithModel
from tokenizer import get_tokenizer

class TextDataset(Dataset):
    def __init__(self, data_path, tokenizer, block_size):
        self.tokenizer = tokenizer
        self.block_size = block_size
        
        # Read all files
        text = ""
        if os.path.isdir(data_path):
            for root, _, files in os.walk(data_path):
                for f in files:
                    if f.endswith(('.cs', '.cpp', '.h', '.hpp', '.txt')):
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                            text += file.read() + "\n"
        else:
            with open(data_path, 'r', encoding='utf-8') as file:
                text = file.read()
                
        self.tokens = tokenizer.encode(text).ids
        print(f"Loaded {len(self.tokens)} tokens from {data_path}")

    def __len__(self):
        return len(self.tokens) - self.block_size

    def __getitem__(self, idx):
        # Grab a chunk of (block_size + 1) tokens
        chunk = self.tokens[idx : idx + self.block_size + 1]
        chunk = torch.tensor(chunk, dtype=torch.long)
        
        x = chunk[:-1]
        y = chunk[1:]
        
        return x, y

def get_action_mask(targets, tokenizer):
    # Create a mask where 1 indicates an action token
    # We need to identify the IDs of action tokens
    action_token_ids = set()
    for token in tokenizer.get_vocab():
        if token.startswith("<ACTION_"):
            action_token_ids.add(tokenizer.token_to_id(token))
            
    mask = torch.zeros_like(targets, dtype=torch.float)
    for action_id in action_token_ids:
        mask = mask + (targets == action_id).float()
    
    return mask

def train():
    # Config
    config = LilithConfig()
    config.n_layer = 4 # Reduced for quick testing
    config.n_head = 4
    config.n_embd = 128
    config.block_size = 64
    batch_size = 4
    max_iters = 50
    learning_rate = 3e-4
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    print(f"Using device: {device}")

    # Load Tokenizer
    try:
        tokenizer = get_tokenizer("lilith_tokenizer.json")
    except:
        print("Tokenizer not found, please run tokenizer.py first.")
        return

    # Dataset
    train_dataset = TextDataset("data", tokenizer, config.block_size)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Model
    config.vocab_size = tokenizer.get_vocab_size()
    model = LilithModel(config)
    model.to(device)
    
    optimizer = model.configure_optimizers(weight_decay=0.1, learning_rate=learning_rate, betas=(0.9, 0.95), device_type=device)

    model.train()
    
    iter_num = 0
    t0 = time.time()
    
    while iter_num < max_iters:
        for X, Y in train_loader:
            if iter_num >= max_iters: break
            
            X, Y = X.to(device), Y.to(device)
            
            # Generate Action Mask
            action_mask = get_action_mask(Y, tokenizer)
            action_mask = action_mask.to(device)
            
            logits, loss = model(X, Y, action_mask)
            
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            
            if iter_num % 10 == 0:
                dt = time.time() - t0
                print(f"iter {iter_num}: loss {loss.item():.4f}, time {dt*1000:.2f}ms")
                t0 = time.time()
            
            iter_num += 1

    print("Training finished.")
    torch.save(model.state_dict(), "lilith_model.pt")

if __name__ == "__main__":
    train()
