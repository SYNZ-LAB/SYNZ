import socket
import struct
import time
import re
from model import NanoSYNZ
import torch
import os
import tts_engine # [NEW] Voice Module
from search_agent import SearchAgent # [NEW] The Internet Eyes

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

# 1.5 Initialize Search & Memory
print("[THE SELF] Connecting to the Global Network...")
searcher = SearchAgent()
from memory_agent import MemoryAgent # [NEW] The Hippocampus
brain = MemoryAgent() # Initialize DB (takes a second to load models)


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

    return None

UNITY_ADDR = None

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

        # [NEW] Detect Body (Unity)
        if "Unity Connected" in user_msg:
             UNITY_ADDR = addr
             print(f"[SYSTEM] Body Connected at {addr}")
             sock.sendto(b"ACK", addr) # Acknowledge
             continue

        # --- 0. Check Feedback ---
        feedback_reply = handle_feedback(user_msg)
        if feedback_reply:
             print(f"[REPLY]: {feedback_reply}")
             sock.sendto(feedback_reply.encode('utf-8'), addr)
             continue # Skip normal processing

        # --- THE ROUTER ---
        # [PHASE 9 UPDATE]: "God Mode" enabled. All traffic goes to Core (Llama 3).
        # We process Search Intent first.
        
        search_triggers = ["price", "news", "weather", "when", "who is", "what is", "search", "google", "find"]
        needs_search = any(t in user_msg.lower() for t in search_triggers)

        context_data = ""
        
        # [NEW] Check Memory (The Hippocampus)
        memories = brain.recall(user_msg)
        if memories:
             context_data += f"\n{memories}\n"

        if needs_search:
                print("[THE SELF] Searching the web first...")
                web_data = searcher.search(user_msg)
                if web_data:
                    context_data = f"\n[SYSTEM_NOTE: Real-time search data]\n{web_data}\n"
        
        # Send everything to Llama-3
        final_query = context_data + user_msg
        
        print("[THE SELF] Sending to Core...")
        logic_reply = query_logic_brain(final_query)
        
        # Fallback if Core is offline
        if "<ERROR" in logic_reply:
             response = f"My brain is offline. ({logic_reply})"
        else:
             response = logic_reply

        # --- Update Memory ---
        last_user_input = user_msg
        last_ai_response = response
        
        # [NEW] Consolidate to Long-Term Memory
        # We save the pair: "User: ... SYNZ: ..."
        brain.remember(f"User: {user_msg}\nSYNZ: {response}")

        # --- 4. TTS Generation (Voice) ---
        print(f"[THE SELF] Vocalizing: '{response}'")
        audio_ready = False
        try:
            # Clean tags if any (e.g. <SASS>)
            clean_text = re.sub(r'<[^>]*>', '', response).strip()
            # Use ABSOLUTE path for Unity to find it easily
            # (Unity project handles absolute paths better than relative if CWD differs)
            audio_path = os.path.join(script_dir, "..", "response.mp3") 
            audio_path = os.path.abspath(audio_path)
            
            success = tts_engine.generate_audio_sync(clean_text, audio_path)
            if success:
                audio_ready = True
        except Exception as e:
            print(f"[WARN] Voice Generation Failed: {e}")

        # 3. Send back to whoever asked (Likely C++ wrapper or Unity)
        # Send Text Response (Text Bubble)
        print(f"[REPLY]: {response}")
        sock.sendto(response.encode('utf-8'), addr)
        
        # Send Audio Signal (The Mouth)
        if audio_ready:
            # We send a specific header so Unity knows it's an event, not text
            # Format: [AUDIO] <AbsPath>
            signal = f"[AUDIO] {audio_path}"
            sock.sendto(signal.encode('utf-8'), addr)
            print(f"[SIGNAL] Sent Voice Command to {addr}")
            
            # [NEW] Also send to Unity Body if known
            if UNITY_ADDR and UNITY_ADDR != addr:
                sock.sendto(signal.encode('utf-8'), UNITY_ADDR)
                print(f"[SIGNAL] Broadcasted Voice to Body at {UNITY_ADDR}")

    except KeyboardInterrupt:
        print("\n[THE SELF] Shutting down gracefully... Bye!")
        break
    except ConnectionResetError:
        print("[WARN] Connection Reset. Someone disconnected violently (Likely Core). Ignoring.")
    except Exception as e:
        print(f"[CRASH]: {e}")
