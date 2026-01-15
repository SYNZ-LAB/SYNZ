import socket
import struct
import time
import re
from model import NanoSYNZ
import torch
import os
import tts_engine # [NEW] Voice Module

# --- Configuration ---
# The Face (Me)
HOST_IP = "127.0.0.1"
FACE_PORT = 8005

# The Core (The Logic Brain)
CORE_IP = "127.0.0.1"
CORE_PORT = 8006 # C++ Core must listen here

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
training_file_path = os.path.join(script_dir, "data", "training_data.txt")

# The Body (Unity)
# (In this architecture, Unity talks to Me, or Core relays to Me. 
# For now assuming Core relays user input to Me on 8005)

print(f"[THE SELF] Awakening on {HOST_IP}:{FACE_PORT}...")

# 1. Load the Personality (NanoSYNZ)
# We need to know vocab size BEFORE init if possible, or init generic then resize? 
# NanoSYNZ structure is fixed by config, but embeddings depend on vocab.
# Ideally we load Meta FIRST.
device = 'cpu'

# (Moving Meta Load UP to here to get vocab_size)
import pickle
try:
    with open(os.path.join(script_dir, 'meta.pkl'), 'rb') as f:
        meta = pickle.load(f)
    print(f"[THE SELF] Vocabulary Loaded. Size: {meta['vocab_size']}")
    stoi = meta['stoi']
    itos = meta['itos']
    vocab_size = meta['vocab_size']
    # Safe Encode
    encode = lambda s: [stoi.get(c, stoi.get(' ', 0)) for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])
except:
    print("[THE SELF] No metadata found. Using default vocab size.")
    vocab_size = 69
    stoi = {}
    itos = {}

model = NanoSYNZ(vocab_size=vocab_size, n_embed=384, block_size=64, n_head=6, n_layer=6)

# Load Weights
model_path = os.path.join(script_dir, "synz_face.pth") # Absolute path
try:
    model.load_state_dict(torch.load(model_path, map_location=device))
    print("[THE SELF] Personality Loaded. I am awake.")
except Exception as e:
    print(f"[THE SELF] No weights found at {model_path}! ({e})")

model.to(device)
model.eval()

# 2. Setup UDP Socket (The Ear)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST_IP, FACE_PORT))
TIMEOUT = 1.0 # [NEW] 1-second Heartbeat
sock.settimeout(TIMEOUT)

def query_logic_brain(text):
    """Asks the C++ Core for help with code/math."""
    print(f"[THE SELF] Asking Logic Brain: '{text}'")
    try:
        # Send to C++ (Port 8006)
        sock.sendto(text.encode('utf-8'), (CORE_IP, CORE_PORT))
        
        # Wait for reply (Blocking for now, simple)
        sock.settimeout(5.0) # 5 second timeout for Logic
        data, _ = sock.recvfrom(4096)
        return data.decode('utf-8')
    except socket.timeout:
        return "<ERROR: Logic Brain Timed Out>"
    except Exception as e:
        return f"<ERROR: {e}>"
    finally:
        sock.settimeout(TIMEOUT) # ALWAYS reset to Heartbeat

# ... (generate_sass, handle_feedback functions omitted for brevity if unchanged)

# ... (inside while True)
# ... (inside while True)

# ... (Meta loaded at top)

def generate_sass(context):
    """Generates a personality response using NanoSYNZ."""
    if not stoi:
        return "I have no vocabulary matrix. Run train_scratch.py first."

    # 1. Encode Context
    # We prefix with "User: " to prompt it correctly if needed, or just raw context
    prompt = f"User: {context}\nSYNZ:"
    try:
        context_idx = torch.tensor(encode(prompt), dtype=torch.long, device=device).unsqueeze(0)
        
        # 2. Generate
        # max_new_tokens=100 (keep it short for chat)
        generated_idx = model.generate(context_idx, max_new_tokens=100)
        
        # 3. Decode
        full_text = decode(generated_idx[0].tolist())
        
        # 4. Extract only the NEW response (after the prompt)
        response = full_text[len(prompt):].strip()
        
        # Stop at newline if it hallucinates multiple lines
        if "\n" in response:
            response = response.split("\n")[0]
            
        return response
    except Exception as e:
        return f"[BRAIN FART] {e}"

# --- 3. RL Memory Buffer ---
last_user_input = ""
last_ai_response = ""

def handle_feedback(user_msg):
    global last_user_input, last_ai_response
    if user_msg.strip() == "!good":
        if last_user_input and last_ai_response:
            # Save to Training Data
            entry = f"\nUser: {last_user_input}\nSYNZ: {last_ai_response}\n"
            with open(training_file_path, "a", encoding="utf-8") as f:
                f.write(entry)
            return "[SYSTEM] Memory Reinforced. Good girl/boy protocol executed."
        else:
            return "[SYSTEM] No memory to reinforce!"
    elif user_msg.strip() == "!bad":
         # Optional: Add to negative buffer or just ignore
         return "[SYSTEM] Memory Discarded. I'll do better next time... baka."
    return None

while True:
    try:
        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            continue # Loop back to check for signals (e.g. KeyboardInterrupt)
        except socket.timeout:
            continue # Loop back to check for signals (e.g. KeyboardInterrupt)

        user_msg = data.decode('utf-8')
        print(f"[USER SAYS]: {user_msg}")

        # --- 0. Check Feedback ---
        feedback_reply = handle_feedback(user_msg)
        if feedback_reply:
             print(f"[REPLY]: {feedback_reply}")
             sock.sendto(feedback_reply.encode('utf-8'), addr)
             continue # Skip normal processing

        # --- THE ROUTER ---
        # 1. Is this a logic question?
        is_code = False
        triggers = ["code", "function", "fix", "loop", "compile", "error", "bug", "implement"]
        if any(t in user_msg.lower() for t in triggers):
            is_code = True

        response = ""

        if is_code:
            # A. Delegate to C++ Core
            print("[THE SELF] Ugh, code. Delegating to Core...")
            logic_reply = query_logic_brain(user_msg)
            
            # B. Wrap it in Personality
            # (In the future, we feed 'logic_reply' into NanoSYNZ to rewrite it)
            response = f"Fine. Here is your fix: \n{logic_reply}\nTry not to break it again. <SASS>"
        else:
            # A. Just Chat
            print("[THE SELF] Just chatting.")
            response = generate_sass(user_msg)

        # --- Update Memory ---
        last_user_input = user_msg
        last_ai_response = response

        # --- 4. TTS Generation (Voice) ---
        print(f"[THE SELF] Vocalizing: '{response}'")
        try:
            # Clean tags if any (e.g. <SASS>)
            clean_text = re.sub(r'<[^>]*>', '', response).strip()
            tts_engine.generate_audio_sync(clean_text, "response.mp3")
        except Exception as e:
            print(f"[WARN] Voice Generation Failed: {e}")

        # 3. Send back to whoever asked (Likely C++ wrapper or Unity)
        print(f"[REPLY]: {response}")
        sock.sendto(response.encode('utf-8'), addr)

    except KeyboardInterrupt:
        print("\n[THE SELF] Shutting down gracefully... Bye!")
        break
    except ConnectionResetError:
        print("[WARN] Connection Reset. Someone disconnected violently (Likely Core). Ignoring.")
    except Exception as e:
        print(f"[CRASH]: {e}")
