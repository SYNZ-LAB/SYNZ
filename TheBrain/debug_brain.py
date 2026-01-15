import torch
import pickle
import os
from model import NanoSYNZ

# Config
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "synz_face.pth")
meta_path = os.path.join(script_dir, "meta.pkl")
device = 'cpu'

print("=== BRAIN DIAGNOSTIC TOOL ===")

# 1. Load Meta
if not os.path.exists(meta_path):
    print("[FAIL] meta.pkl not found!")
    exit()

with open(meta_path, 'rb') as f:
    meta = pickle.load(f)

vocab_size = meta['vocab_size']
stoi = meta['stoi']
itos = meta['itos']
print(f"[PASS] Meta Loaded. Vocab Size: {vocab_size}")
print(f"[INFO] First 10 chars: {list(stoi.keys())[:10]}")

# 2. Load Model
if not os.path.exists(model_path):
    print("[FAIL] synz_face.pth not found!")
    exit()

model = NanoSYNZ(vocab_size=vocab_size, n_embed=384, block_size=64, n_head=6, n_layer=6)
try:
    model.load_state_dict(torch.load(model_path, map_location=device))
    print("[PASS] Weights Loaded.")
except Exception as e:
    print(f"[FAIL] Weight mismatch or load error: {e}")
    exit()

model.to(device)
model.eval()

# 3. Test Generation
prompt = "User: Hello\nSYNZ:"
print(f"\n[TEST] Prompting with: '{prompt.strip()}'")

encode = lambda s: [stoi.get(c, stoi.get(' ', 0)) for c in s] # Safe encode
decode = lambda l: ''.join([itos[i] for i in l])

idx = torch.tensor(encode(prompt), dtype=torch.long, device=device).unsqueeze(0)
generated = model.generate(idx, max_new_tokens=50)
output = decode(generated[0].tolist())

print(f"\n[OUTPUT]:\n{output}\n")
print("=============================")
if "User:" in output:
    print("[CONCLUSION] Model structure seems preserved.")
else:
    print("[CONCLUSION] Model might be babbling.")
