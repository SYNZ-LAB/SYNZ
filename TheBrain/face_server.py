import socket
import struct
import time
import re
from model import NanoSYNZ
import torch

# --- Configuration ---
# The Face (Me)
HOST_IP = "127.0.0.1"
FACE_PORT = 8005

# The Core (The Logic Brain)
CORE_IP = "127.0.0.1"
CORE_PORT = 8006 # C++ Core must listen here

# The Body (Unity)
# (In this architecture, Unity talks to Me, or Core relays to Me. 
# For now assuming Core relays user input to Me on 8005)

print(f"[THE SELF] Awakening on {HOST_IP}:{FACE_PORT}...")

# 1. Load the Personality (NanoSYNZ)
device = 'cpu'
model = NanoSYNZ(vocab_size=69, n_embed=384, block_size=64, n_head=6, n_layer=6)
# Load Weights (If they exist)
try:
    model.load_state_dict(torch.load("synz_face.pth", map_location=device))
    print("[THE SELF] Personality Loaded. I am awake.")
except:
    print("[THE SELF] No weights found! Am I a ghost? (Training needed)")
    # We continue anyway for testing

model.to(device)
model.eval()

# 2. Setup UDP Socket (The Ear)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST_IP, FACE_PORT))

def query_logic_brain(text):
    """Asks the C++ Core for help with code/math."""
    print(f"[THE SELF] Asking Logic Brain: '{text}'")
    try:
        # Send to C++ (Port 8006)
        sock.sendto(text.encode('utf-8'), (CORE_IP, CORE_PORT))
        
        # Wait for reply (Blocking for now, simple)
        sock.settimeout(5.0) # 5 second timeout
        data, _ = sock.recvfrom(4096)
        sock.settimeout(None)
        return data.decode('utf-8')
    except socket.timeout:
        return "<ERROR: Logic Brain Timed Out>"
    except Exception as e:
        return f"<ERROR: {e}>"

def generate_sass(context):
    """Generates a personality response using NanoSYNZ."""
    # (Placeholder wrapper for model.generate)
    # In reality, we encode 'context', run generate(), decode.
    # For this prototype, we mock it if model is untrained.
    return f"I processed: '{context}' but I'm just a demo right now. <SASS>"

while True:
    try:
        data, addr = sock.recvfrom(1024)
        user_msg = data.decode('utf-8')
        print(f"[USER SAYS]: {user_msg}")

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

        # 3. Send back to whoever asked (Likely C++ wrapper or Unity)
        print(f"[REPLY]: {response}")
        sock.sendto(response.encode('utf-8'), addr)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"[CRASH]: {e}")
