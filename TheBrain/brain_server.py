import json
import socket
import time
import os
import glob
from llama_cpp import Llama
import win32pipe, win32file, pywintypes
import threading

# --- Config ---
HOST_IP = "127.0.0.1"
CORE_PORT = 8006

import sys

# Resolve Paths (Support PyInstaller)
if getattr(sys, 'frozen', False):
    # Running as compiled EXE
    SCRIPT_DIR = os.path.dirname(sys.executable)
    # Check if we are in OneDir mode (dist/brain/brain.exe) -> Models in ../models
    if os.path.exists(os.path.join(SCRIPT_DIR, "..", "models")):
        PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Go up
    else:
        PROJECT_ROOT = SCRIPT_DIR # OneFile mode
else:
    # Running as Script
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Go up to SYNZ root

MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "Llama-3.1-8B-Instruct-Q6_K.gguf")
UNITY_SCRIPTS_PATH = os.path.join(PROJECT_ROOT, "unity_scripts")
UNITY_LOG_PATH = os.path.expandvars(r"%LOCALAPPDATA%\Unity\Editor\Editor.log")
PIPE_NAME = r'\\.\pipe\SYNZ_NeuroLink'

# Colors
from colorama import init, Fore
init(autoreset=True)
C_BRAIN = Fore.MAGENTA
C_ERR = Fore.RED

print(f"{C_BRAIN}[BRAIN] Booting Python Logic Core...")

# 1. Load Model
try:
    print(f"{C_BRAIN}[BRAIN] Loading Llama-3 (This takes a moment)...")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=8192, # [UPGRADE] Quadrupled Context Limit (Better Memory)
        n_gpu_layers=-1, # [OPT] Auto-detect Max GPU Layers (Speed)
        chat_format="llama-3", # [FIX] Force Llama-3 format
        verbose=False
    )
    print(f"{C_BRAIN}[BRAIN] Model Online.")
except Exception as e:
    print(f"{C_ERR}[CRASH] Model Load Failed: {e}")
    # Fallback or exit?
    llm = None

# 2. Named Pipe Server (NeuroLink to Unity)
pipe_handle = None

def create_pipe():
    global pipe_handle
    try:
        pipe_handle = win32pipe.CreateNamedPipe(
            PIPE_NAME,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65536, 65536,
            0,
            None
        )
        print(f"{C_BRAIN}[BRAIN] NeuroLink Pipe Created. Waiting for Unity...")
        # Client connects lazily
    except Exception as e:
        print(f"{C_ERR}[BRAIN] Pipe Error: {e}")

def send_to_unity(msg):
    global pipe_handle
    if not pipe_handle: return
    try:
        # Check if connected (This is tricky with win32, often we just write)
        # We assume Unity Connects. 
        # In a real server, we'd accept connection. 
        # For simplicity, we just try to WriteFile.
        # Note: CreateNamedPipe expects a ConnectNamedPipe call.
        pass 
    except:
        pass

# Simple Pipe Wrapper using win32file because basic Write is blocking
# Replacing complex Pipe logic with a Helper Thread is better, 
# but for now let's just use UDP to Face, and Face to Unity?
# Use UDP to 8005 (Face) simplifies things.
# But CodeMonitor needs to talk to Unity Console.
# Let's keep it simple: Logic -> Face (8005). Face -> Unity (UDP).
# We can skip the Named Pipe for now to avoid 'pywin32' complexity if user fails install.
# BUT main.cpp had it.
# Let's pivot: We will send EVERYTHING to Face Server (8005), and Face Server Relays to Unity.
# Face Server is already set up to talk to Unity via UDP.
# So we drop the Named Pipe here.

# 3. File Watchers
file_stamps = {}
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mentor_config.json"))

# Default Config (Fallback)
WATCH_CONFIG = {
    "watch_paths": [os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))],
    "allowed_extensions": ['.cs', '.py', '.cpp', '.h', '.bat', '.cmake', '.txt'],
    "ignored_dirs": ['venv', '.git', 'Library', 'Temp', 'Build', 'obj', '__pycache__', '.vs']
}

# Load Config
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'r') as f:
            user_config = json.load(f)
            # Merge/Overwrite
            if "watch_paths" in user_config: WATCH_CONFIG["watch_paths"] = user_config["watch_paths"]
            if "allowed_extensions" in user_config: WATCH_CONFIG["allowed_extensions"] = set(user_config["allowed_extensions"])
            if "ignored_dirs" in user_config: WATCH_CONFIG["ignored_dirs"] = set(user_config["ignored_dirs"])
            print(f"{C_BRAIN}[CONFIG] Loaded Monitor Config. Watching: {len(WATCH_CONFIG['watch_paths'])} paths.")
    except Exception as e:
        print(f"{C_ERR}[CONFIG] Failed to load mentor_config.json: {e}")

def check_code():
    global file_stamps
    changes = []
    
    # Iterate over all configured paths
    for base_path in WATCH_CONFIG["watch_paths"]:
        # Resolve full path (handle '.' or relative paths)
        if base_path == ".": base_path = os.path.dirname(CONFIG_PATH) # Root of SYNZ
        
        if not os.path.exists(base_path): continue

        for root, dirs, files in os.walk(base_path):
            # Filter Directories (Modify in-place)
            dirs[:] = [d for d in dirs if d not in WATCH_CONFIG["ignored_dirs"]]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in WATCH_CONFIG["allowed_extensions"]:
                    full_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(full_path)
                        
                        if full_path not in file_stamps:
                            file_stamps[full_path] = mtime
                        elif file_stamps[full_path] != mtime:
                            # File Changed!
                            file_stamps[full_path] = mtime
                            # [FIX] Use absolute path for clarity in Multi-Project setup
                            print(f"{C_BRAIN}[WATCHER] Code Changed: {full_path}")
                            
                            # Read content
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                 content = f.read()
                                 changes.append(f"FILE: {full_path}\n{content[:5000]}")
                                 
                    except Exception:
                        continue
    
    if changes:
        return "\n\n".join(changes)
    return None

last_log_pos = 0

def check_logs():
    global last_log_pos
    if not os.path.exists(UNITY_LOG_PATH): return None
    
    try:
        current_size = os.path.getsize(UNITY_LOG_PATH)
        if current_size < last_log_pos: last_log_pos = 0 # Log rotated
        
        if current_size > last_log_pos:
            with open(UNITY_LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_log_pos)
                new_data = f.read()
                last_log_pos = current_size
                return new_data
    except:
        pass
    return None

# 4. Main Loop
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # [FIX] Allow port reuse on restart
sock.bind((HOST_IP, CORE_PORT))
sock.setblocking(False)

FACE_ADDR = (HOST_IP, 8005)


print(f"{C_BRAIN}[BRAIN] Logic Core Listening on {CORE_PORT}...")
MENTOR_MODE = False # [FEATURE] Manual Toggle for Code Mentor


while True:
    try:
        # A. Network Request (From Face)
        try:
            data, addr = sock.recvfrom(65535) # Increased from 4096 to prevent WinError 10040
            decoded_data = data.decode('utf-8')
            

            # [FIX] Ignore "Ready" loop signals
            decoded_lower = decoded_data.lower()
            if "i am ready" in decoded_lower or "i'm ready" in decoded_lower:
                print(f"{C_BRAIN}[IGNORE] Blocked 'Ready' Loop Signal.")
                continue

            # [FEATURE] Mentor Mode Toggle
            if "activate code mentor" in decoded_lower or "enable code mentor" in decoded_lower:
                MENTOR_MODE = True
                msg = "[SYSTEM] Code Mentor Activated. I will now review your changes."
                sock.sendto(msg.encode('utf-8'), addr)
                print(f"{C_BRAIN}[CMD] Mentor Mode: ON")
                continue
            elif "stop code mentor" in decoded_lower or "disable code mentor" in decoded_lower:
                MENTOR_MODE = False
                msg = "[SYSTEM] Code Mentor Deactivated."
                sock.sendto(msg.encode('utf-8'), addr)
                print(f"{C_BRAIN}[CMD] Mentor Mode: OFF")
                continue


            messages = []
            
            # [FIX] Try to parse as JSON first (Structured Chat)
            try:
                packet = json.loads(decoded_data)
                
                # 1. System Prompt
                if "system" in packet:
                    messages.append({"role": "system", "content": packet["system"]})
                    
                # 2. History (List of {role, content})
                if "history" in packet and isinstance(packet["history"], list):
                    messages.extend(packet["history"])
                    
                # 3. User Input
                if "user" in packet:
                    messages.append({"role": "user", "content": packet["user"]})
                    
                print(f"{C_BRAIN}[REQ] Structured Chat ({len(messages)} msgs)...")
                
            except json.JSONDecodeError:
                # Fallback: Legacy String Mode
                prompt = decoded_data
                messages = [{"role": "user", "content": prompt}]
                print(f"{C_BRAIN}[REQ] Legacy Prompt...")
            
            # Inference
            # Inference
            last_msg_content = messages[-1]['content'] if messages else "???"
            # Clean up newlines for log readability
            readable_msg = last_msg_content.replace('\n', ' ')[:80] 
            print(f"{C_BRAIN}[REQ] User: '{readable_msg}...' (Hist: {len(messages)})")
            # print(f"{C_BRAIN}[DEBUG] Full Context Sent.") # Disabled for readability
            output = llm.create_chat_completion(
                messages=messages, # [FIX] Restored missing argument
                temperature=0.7,
                top_p=0.9,
                repeat_penalty=1.25, # [TUNED] Relaxed from 1.3 for better fluency
                stop=["<|eot_id|>"]
            )
            response = output['choices'][0]['message']['content']
            
            # [FIX] Clean Generation Artifacts
            # Llama-3 sometimes includes the speaker label in the output
            if response.startswith("SYNZ:"): response = response[5:].strip()
            elif response.startswith("Assistant:"): response = response[10:].strip()
            elif response.startswith("User:"): response = response[5:].strip() # Hallucinating user turn
            
            # [FIX] Anti-Parrot Guard
            # If Model just repeats the User, we intercept it.
            # We use 'raw_user' from packet if available, otherwise fallback to messages[-1]
            check_against = ""
            if "raw_user" in packet:
                check_against = packet["raw_user"].strip().lower()
            else:
                check_against = messages[-1]['content'].strip().lower()

            if response.strip().lower() == check_against:
                print(f"{C_ERR}[GUARD] Blocked Parrot Response ('{response}'). forcing fallback.")
                response = "I am SYNZ. I am listening."
            elif response.strip() == "":
                 response = "..."
            
            # Reply
            print(f"{C_BRAIN}[ANS] {response[:50]}...")
            sock.sendto(response.encode('utf-8'), addr)
            
        except BlockingIOError:
            pass

        if MENTOR_MODE:
            code_diff = check_code()
            if code_diff:
                # [UPGRADE] Mentor Mode Prompt (Helpful Edition)
                prompt = (
                    f"You are a Senior Developer. The user just updated this code:\n"
                    f"{code_diff}\n\n"
                    f"1. Briefly explain what changed.\n"
                    f"2. If there are bugs, teach the user how to fix them.\n"
                    f"3. If it looks good, give a quick compliment.\n"
                    f"Keep it short and helpful."
                )
                output = llm.create_chat_completion(messages=[{"role": "user", "content": prompt}])
                feedback = output['choices'][0]['message']['content']
                print(f"{C_BRAIN}[MENTOR] {feedback[:50]}...")
                
                # Send to Face (Use unique tag so we can whitelist it for TTS)
                msg = f"[CODE_MENTOR]: {feedback}"
                sock.sendto(msg.encode('utf-8'), FACE_ADDR)

        # C. Check Logs (Smart Sentinel)
        logs = check_logs()
        if logs and ("Error" in logs or "Exception" in logs):
             # [FIX] Anti-Spam: Don't report the exact same log chunk twice
             # We rely on 'check_logs' returning new data, but if the error implies a generic state...
             # Actually check_logs output is already diff-based? 
             # No, check_logs reads from last_log_pos. So it's ALWAYS new data.
             # BUT Unity might spam the same error 60 times a second.
             
             # Heuristic: deduplicate lines? Or just report summary.
             # For now, we trust the LLM to summarize, but we limit frequency?
             # Let's just run it. check_logs only returns NEW appended content. 
             # If Unity spams 1000 lines of NullRef, we get a huge chunk.
             
             # Truncate to last 1000 chars to save tokens
             log_snippet = logs[-1000:]
             
             print(f"{C_BRAIN}[SENTINEL] analyzing new errors...")
             prompt = f"Analyze this UNITY LOG ERROR concisely:\n{log_snippet}\nExplain what is broken."
             
             try:
                 output = llm.create_chat_completion(
                     messages=[{"role": "user", "content": prompt}],
                     max_tokens=100, # Keep it short
                     temperature=0.5
                 )
                 feedback = output['choices'][0]['message']['content']
                 print(f"{C_BRAIN}[LOGS] {feedback}")
                 
                 # Send to Face (System Event)
                 msg = f"[SYSTEM_EVENT: Log Watcher]: {feedback}"
                 sock.sendto(msg.encode('utf-8'), FACE_ADDR)
             except Exception as e:
                 print(f"{C_ERR}[LOG ERR] {e}")

        time.sleep(0.1)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"{C_ERR}[ERR] {e}")
