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

# Resolve paths relative to THIS script (TheBrain/brain_server.py)
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
        n_ctx=2048,
        n_gpu_layers=35, # Attempt GPU offload
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

def check_code():
    global file_stamps
    changes = []
    
    if not os.path.exists(UNITY_SCRIPTS_PATH): return None

    # Scan .cs files
    files = glob.glob(os.path.join(UNITY_SCRIPTS_PATH, "*.cs"))
    for f in files:
        mtime = os.path.getmtime(f)
        if f not in file_stamps:
            file_stamps[f] = mtime
        elif file_stamps[f] != mtime:
            file_stamps[f] = mtime
            print(f"{C_BRAIN}[WATCHER] Code Changed: {os.path.basename(f)}")
            with open(f, 'r', encoding='utf-8') as code_file:
                 changes.append(code_file.read())
    
    if changes:
        return "\n".join(changes)
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
sock.bind((HOST_IP, CORE_PORT))
sock.setblocking(False)

FACE_ADDR = (HOST_IP, 8005)

print(f"{C_BRAIN}[BRAIN] Logic Core Listening on {CORE_PORT}...")

while True:
    try:
        # A. Network Request (From Face)
        try:
            data, addr = sock.recvfrom(65535) # Increased from 4096 to prevent WinError 10040
            decoded_data = data.decode('utf-8')
            
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
            output = llm.create_chat_completion(
                messages=messages,
                max_tokens=150,
                temperature=0.7,
                top_p=0.9,
                repeat_penalty=1.1
            )
            response = output['choices'][0]['message']['content']
            
            # Reply
            print(f"{C_BRAIN}[ANS] {response[:50]}...")
            sock.sendto(response.encode('utf-8'), addr)
            
        except BlockingIOError:
            pass

        # B. Check Code
        code_diff = check_code()
        if code_diff:
            prompt = f"REVIEW THIS CODE:\n{code_diff}\nIdentify any bugs briefly."
            output = llm.create_chat_completion(messages=[{"role": "user", "content": prompt}])
            feedback = output['choices'][0]['message']['content']
            print(f"{C_BRAIN}[SENTINEL] {feedback}")
            # Send to Face (who will speak it)
            msg = f"[SYSTEM_EVENT: Code Watcher]: {feedback}"
            sock.sendto(msg.encode('utf-8'), FACE_ADDR)

        # C. Check Logs (DISABLED to prevent spam during voice testing)
        # logs = check_logs()
        # if logs and ("Error" in logs or "Exception" in logs):
        #      prompt = f"Using this UNITY LOG, explain the error:\n{logs[-500:]}"
        #      output = llm.create_chat_completion(
        #          messages=[{"role": "user", "content": prompt}],
        #          max_tokens=150,
        #          temperature=0.7,
        #          top_p=0.9,
        #          repeat_penalty=1.1
        #      )
        #      feedback = output['choices'][0]['message']['content']
        #      print(f"{C_BRAIN}[LOGS] {feedback}")
        #      msg = f"[SYSTEM_EVENT: Log Watcher]: {feedback}"
        #      sock.sendto(msg.encode('utf-8'), FACE_ADDR)

        time.sleep(0.1)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"{C_ERR}[ERR] {e}")
