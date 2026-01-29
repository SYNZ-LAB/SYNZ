import json
import socket
import struct
import time
import re
from model import NanoSYNZ
import torch
import os
import tts_engine # [NEW] Voice Module
from search_agent import SearchAgent # [NEW] The Internet Eyes

# [NEW] QoL: Colors
from colorama import init, Fore, Style
init(autoreset=True)
C_SELF = Fore.GREEN
C_USER = Fore.CYAN
C_SYS = Fore.YELLOW
C_CORE = Fore.MAGENTA
C_ERR = Fore.RED


# --- Configuration ---
# The Face (Me)
HOST_IP = "127.0.0.1"
FACE_PORT = 8005

# The Core (The Logic Brain)
CORE_IP = "127.0.0.1"
CORE_PORT = 8006 # C++ Core must listen here

# The Ears (Microphone)
EARS_ADDR = ("127.0.0.1", 8007)

def mute_ears(seconds=5.0):
    try:
        sock.sendto(f"MUTE {seconds}".encode('utf-8'), EARS_ADDR)
    except:
        pass

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

# 1.5 Initialize Search, Memory, Vision, & Hands
print("[THE SELF] Connecting to the Global Network...")
searcher = SearchAgent()

from memory_agent import MemoryAgent # [NEW] The Hippocampus
brain = MemoryAgent() 

# [NEW] Phase 15: The Hands
from editor_agent import EditorAgent
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Go up one level from 'TheBrain'
hands = EditorAgent(root_dir=project_root)

# [NEW] Phase 12: Vision
try:
    from sight import SightAgent
    eyes = SightAgent()
except ImportError:
    print("[THE SELF] Vision Module disabled (Missing dependencies).")
    eyes = None
except Exception as e:
    print(f"[THE SELF] Blinded: {e}")
    eyes = None


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
        sock.settimeout(30.0) # 30 second timeout for Logic (Llama-3 is slow on CPU)
        data, _ = sock.recvfrom(65535) # Increased from 4096 to avoid WinError 10040
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
conversation_history = [] # [NEW] Short Term Memory Buffer

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

    return None

UNITY_ADDR = None

# --- [NEW] Phase 14: Agency (The Watcher) ---
import random
last_interaction = time.time()
AGENCY_THRESHOLD = 600 # 10 Minutes (Test with 30s if you want)
proactive_triggers = [
    "You have been quiet for a while. Are you stuck?",
    "Hey! Drink some water.",
    "I'm bored. Let's code something.",
    "Do you want me to search for new AI papers?"
]

def check_agency():
    """Checks if we should take initiative."""
    global last_interaction
    silence = time.time() - last_interaction
    
    if silence > AGENCY_THRESHOLD:
        # Reset timer so we don't spam
        last_interaction = time.time() 
        topic = random.choice(proactive_triggers)
        
        # We need to INJECT this into the loop as if it came from Core,
        # OR just speak it directly. Speaking directly is easier.
        print(f"[AGENCY] Proactive Event Triggered: {topic}")
        return topic
    return None

while True:
    try:
        # 0. Check Agency (Proactive Check-in)
        # proactive_msg = check_agency() 
        # (Disabled for stability for now)

        # 1. Wait for Network Request
        try:
             data, addr = sock.recvfrom(65535)
             user_msg = data.decode('utf-8').strip()
        except socket.timeout:
             continue
        except Exception as e:
             print(f"{C_ERR}[NET ERR] {e}")
             continue

        # [FIX] Traffic Control
        # If message comes from the Brain (8006), it's a System Event (e.g. Sentinel).
        # We must NOT reply to 8006. We must speak to the User (Unity).
        if addr[1] == CORE_PORT:
             print(f"{C_CORE}[EVENT] Received from Brain: {user_msg}")
             if UNITY_ADDR:
                  addr = UNITY_ADDR # Redirect reply to User
             else:
                  print(f"{C_ERR}[WARN] Brain wants to speak, but no Body (Unity) connected.")
                  continue # Drop it


        # [NEW] Detect Body (Unity)
        if "unity connected" in user_msg.lower():
             UNITY_ADDR = addr
             print(f"{C_SYS}[SYSTEM] Body Connected at {addr}")
             sock.sendto(b"ACK", addr) # Acknowledge
             # [FIX] Do NOT treat this as a user query, or we loop forever.
             continue
        
        # [FIX] Filter System Events from Chat History & Voice
        # If it's a Log Watcher event, we process it but DO NOT add to history or speak immediately unless critical.
        is_system_event = user_msg.startswith("[SYSTEM_EVENT")

        # --- 0. Check Feedback ---
        feedback_reply = handle_feedback(user_msg)
        if feedback_reply:
             print(f"[REPLY]: {feedback_reply}")
             sock.sendto(feedback_reply.encode('utf-8'), addr)
             continue # Skip normal processing

        # --- [NEW] Phase 15: The Hands (Direct Tools) ---
        if user_msg.startswith("!read "):
             filename = user_msg[6:].strip()
             print(f"[THE HANDS] Reading {filename}...")
             content = hands.read_file(filename)
             # Truncate if too long for UDP? 
             # For now, just send first 4096 bytes or full content
             reply = f"[FILE CONTENT]:\n{content[:2000]}..." if len(content) > 2000 else content
             sock.sendto(reply.encode('utf-8'), addr)
             continue
        
        elif user_msg.startswith("!write "):
             # Format: !write filename|content
             parts = user_msg[7:].split("|", 1)
             if len(parts) == 2:
                  filename, content = parts[0].strip(), parts[1]
                  print(f"[THE HANDS] Writing to {filename}...")
                  reply = hands.write_file(filename, content)
                  sock.sendto(reply.encode('utf-8'), addr)
             else:
                  sock.sendto("[ERR] Usage: !write filename|content".encode('utf-8'), addr)
             continue
        
        elif user_msg.startswith("!run "):
             filename = user_msg[5:].strip()
             print(f"{C_SELF}[THE HANDS] Running {filename}...")
             
             # Execute
             reply = hands.run_file(filename)
             print(f"{C_SYS}[RUN RESULT]:\n{reply}")
             
             # --- [NEW] The Reflex Loop ---
             # Don't just show output. React to it.
             # We construct a new "internal thought" prompt.
             
             if "[FAIL]" in reply:
                 reflex_prompt = f"SYSTEM_EVENT: I ran '{filename}' but it failed with this output:\n{reply}\n\nTASK: Explain the error simply to the user (like a teacher) and immediately use !write to fix it."
             else:
                 reflex_prompt = f"SYSTEM_EVENT: I ran '{filename}' successfully. Output:\n{reply}\n\nTASK: Tell the user it worked and explain what the code did."

             # Recurse: Send THIS prompt to the Logic Brain as if it was my own thought
             # We bypass the 'user_msg' loop and jump straight to logic processing
             print(f"{C_SELF}[REFLEX] Analyzing execution result...")
             
             # We reuse the logic block below to get a personality response
             # Hack: Set user_msg to reflex_prompt and let it flow down
             user_msg = reflex_prompt
             # Remove [SYSTEM_EVENT] tag for the user display? No, keep it internal.
             
             # Let it fall through to the 'context_data' logic below...
             pass 


        # --- THE ROUTER ---
        # [PHASE 9 UPDATE]: "God Mode" enabled. All traffic goes to Core (Llama 3).
        # We process Search Intent first.
        
        search_triggers = ["price", "news", "weather", "when", "who is", "what is", "search", "google", "find"]
        needs_search = any(t in user_msg.lower() for t in search_triggers)

        context_data = ""
        
        # [NEW] Phase 12: Vision Check
        if "look" in user_msg.lower() or "see" in user_msg.lower():
             if eyes:
                 print(f"{C_SELF}[THE SELF] Opening Eyes...")
                 vision_desc = eyes.analyze(user_msg)
                 context_data += f"\n{vision_desc}\n"
             else:
                 context_data += "\n[SYSTEM_NOTE: User asked to see, but Vision is disabled/blind.]\n"

        # [NEW] Check Memory (The Hippocampus)
        memories = brain.recall(user_msg)
        if memories:
             context_data += f"\n{memories}\n"

        if needs_search:
                print(f"{C_SELF}[THE SELF] Searching the web first...")
                web_data = searcher.search(user_msg)
                if web_data:
                    context_data = f"\n[SYSTEM_NOTE: Real-time search data]\n{web_data}\n"
        
        # [NEW] Local History Buffer (Short Term Memory)
        # Required because Vector DB might be offline
        history_text = "\n".join(conversation_history[-6:]) # Last 3 turns
        
        # [NEW] System Identity & Instructions
        # [NEW] System Identity & Instructions
        SYSTEM_PROMPT = (
            "You are SYNZ, an AI assistant. "
            "Your Goal: Answer the user's questions meaningfully and helpfully.\n"
            "RULES:\n"
            "1. NEVER repeat the user's input.\n"
            "2. If asked 'Who are you?', reply: 'I am SYNZ.'\n"
            "3. Be concise."
        )

        # Send everything to Llama-3
        # [FIX] Send STRUCTURED JSON so Llama-3 knows who is who.
        
        # 1. Convert History List [ "User: Hi", "SYNZ: Hello" ] -> List of Dicts
        chat_format_history = []
        for line in conversation_history:
            if line.startswith("User: "):
                chat_format_history.append({"role": "user", "content": line[6:]})
            elif line.startswith("SYNZ: "):
                chat_format_history.append({"role": "assistant", "content": line[6:]})

        # 2. Build Packet
        packet = {
            "system": SYSTEM_PROMPT,
            "history": chat_format_history,
            "user": f"{context_data}\n\n{user_msg}" # Context attaches to current turn
        }
        
        final_query = json.dumps(packet)
        
        print(f"{C_CORE}[THE SELF] Sending structured thought to Core...")
        logic_reply = query_logic_brain(final_query)
        
        # Fallback if Core is offline
        if "<ERROR" in logic_reply:
             response = f"My brain is offline. ({logic_reply})"
        else:
             # [PHASE 16: HYBRID BRAIN RESTORATION]
             # logic_reply contains the FACTUAL answer from Llama-3.
             # We now feed this into YOUR Custom Transformer (NanoSYNZ) to apply personality/style.
             
             print(f"{C_SELF}[THE SELF] Applying Personality Filter (NanoSYNZ)...")
             
             # Context for NanoSYNZ: "Here is the fact: {fact}. Rewrite it as SYNZ."
             # Note: NanoSYNZ needs to be trained on this pattern to work well.
             # For now, we will try to just prompt it with the user context + logic answer.
             
             # However, since NanoSYNZ is currently very small/untrained on this specific task, 
             # forcing it might degrade the answer to gibberish. 
             # SAFE MODE: We stick to Llama-3 for now until you run 'train_scratch.py' with new data.
             
             # UNCOMMENT BELOW TO ENABLE HYBRID MODE ONCE TRAINED:
             # style_prompt = f"Fact: {logic_reply}\nSYNZ style:"
             # styled_response = generate_sass(style_prompt)
             # response = styled_response
             
             # CURRENT: Llama-3 does both Logic + Personality (via System Prompt)
             response = logic_reply
             
             # [FIX] Face-Level Anti-Parrot Block
             # Sometimes Brain fails to catch it.
             clean_resp = response.lower().strip()
             clean_user = user_msg.lower().strip()
             
             if clean_resp == clean_user:
                  print(f"{C_ERR}[FACE] Blocked Parrot Response! Override.")
                  response = "I am listening."
             elif "unity connected" in clean_resp:
                  print(f"{C_ERR}[FACE] Blocked 'Unity Connected' Hallucination.")
                  response = "I am ready." # Safe fallback
             elif len(response) < 2:
                  response = "..."
             
        # Update History (Only for real user interactions, not system dumps)
        if not is_system_event:
            conversation_history.append(f"User: {user_msg}")
            conversation_history.append(f"SYNZ: {response}")
            if len(conversation_history) > 20: conversation_history.pop(0) # Keep buffer small

        # --- Update Memory ---
        last_user_input = user_msg
        last_ai_response = response
        
        # Reset Agency Timer
        last_interaction = time.time()
        
        # [NEW] Consolidate to Long-Term Memory
        # We save the pair: "User: ... SYNZ: ..."
        if not is_system_event:
            brain.remember(f"User: {user_msg}\nSYNZ: {response}")

        # --- 4. TTS Generation (Voice) ---
        audio_ready = False
        
        # [FIX] Don't vocalize internal system logs (like error reports), only user interactions
        if not is_system_event:
            print(f"{C_SELF}[THE SELF] Vocalizing: '{response}'")
            try:
                # Clean tags if any (e.g. <SASS>)
                clean_text = re.sub(r'<[^>]*>', '', response).strip()
                # Use ABSOLUTE path for Unity to find it easily
                audio_path = os.path.join(script_dir, "..", "response.mp3") 
                audio_path = os.path.abspath(audio_path)
                
                # [FIX] Delete previous if exists to force fresh write
                if os.path.exists(audio_path):
                    try: os.remove(audio_path)
                    except: pass

                # [FIX] Mute Ears to prevent feedback loop (Hearing myself)
                duration = max(3.0, len(clean_text) / 10.0) # Conservative estimate
                mute_ears(duration)
                print(f"{C_SYS}[THE SELF] Muting ears for {duration:.1f}s...")

                success = tts_engine.generate_audio_sync(clean_text, audio_path)
                
                # [FIX] Verify Integrity
                if success and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                    time.sleep(0.3) # Increased to 0.3s to ensure file handle is released for Unity
                    audio_ready = True
                else:
                     print(f"{C_ERR}[WARN] Audio file generation failed or empty.")
                     audio_ready = False
                     
            except Exception as e:
                print(f"{C_ERR}[WARN] Voice Generation Failed: {e}")
        else:
            print(f"{C_SYS}[THE SELF] (Internal Event - Voice Muted)")

        # 3. Send back to whoever asked (Likely C++ wrapper or Unity)
        # Send Text Response (Text Bubble)
        print(f"{C_SELF}[REPLY]: {response}")
        try:
            sock.sendto(response.encode('utf-8'), addr)
        except OSError as e:
            if e.winerror == 10054:
                print(f"{C_ERR}[WARN] Client Disconnected (10054)")
            else:
                print(f"{C_ERR}[NET ERR] {e}")
        
        # Send Audio Signal (The Mouth)
        if audio_ready:
            # We send a specific header so Unity knows it's an event, not text
            # Format: [AUDIO] <AbsPath>
            signal = f"[AUDIO] {audio_path}"
            sock.sendto(signal.encode('utf-8'), addr)
            print(f"{C_SYS}[SIGNAL] Sent Voice Command to {addr}")
            
            # [NEW] Also send to Unity Body if known
            if UNITY_ADDR and UNITY_ADDR != addr:
                sock.sendto(signal.encode('utf-8'), UNITY_ADDR)
                print(f"{C_SYS}[SIGNAL] Broadcasted Voice to Body at {UNITY_ADDR}")

    except KeyboardInterrupt:
        print(f"\n{C_SYS}[THE SELF] Shutting down gracefully... Bye!")
        break
    except ConnectionResetError:
        print(f"{C_ERR}[WARN] Connection Reset. Someone disconnected violently (Likely Core). Ignoring.")
    except Exception as e:
        print(f"{C_ERR}[CRASH]: {e}")
