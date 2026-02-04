import sounddevice as sd
import numpy as np
import whisper
import socket
import time
import queue
import queue
import scipy.io.wavfile as wav
import winsound # [NEW] For startup chime

# --- Configuration ---
HOST_IP = "127.0.0.1"
HOST_PORT = 8005
SAMPLE_RATE = 16000
BLOCK_SIZE = 4000 
THRESHOLD = 0.01 # [TUNED] Reverted to 0.01 to avoid fan noise
SILENCE_DURATION = 0.8 # [TUNED] Increased slightly to prevent chopping

# --- Paths & Model ---
import sys
import os

if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
    # OneDir support (dist/ears/ears.exe -> ../models)
    if os.path.exists(os.path.join(SCRIPT_DIR, "..", "models")):
        SCRIPT_DIR = os.path.dirname(SCRIPT_DIR)
    # PyInstaller Bundle Root
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Only valid if script is in TheBrain/. Adjust for logic.
# Actually, if in TheBrain/ears.py, root is ../
# But if frozen, SCRIPT_DIR is the dist folder where we put models.
# So we assume 'models' is next to executable.

LOCAL_MODEL_PATH = os.path.join(SCRIPT_DIR, "models", "small.en.pt")

print("[EARS] Loading Model...")
if os.path.exists(LOCAL_MODEL_PATH):
    print(f"[EARS] Found local model: {LOCAL_MODEL_PATH}")
    model = whisper.load_model(LOCAL_MODEL_PATH)
else:
    print("[EARS] Local model not found. Downloading 'small.en'...")
    model = whisper.load_model("small.en")
print("[EARS] Model Loaded. Listening...")
winsound.Beep(1000, 200) # [NEW] Startup Chime (High Pitch)
winsound.Beep(1500, 200)

# [NEW] Hallucination Filters (Common Whisper Artifacts)
HALLUCINATION_FILTERS = {
    "thanks for watching", "thank you for watching", "watching", 
    "you", ".", "i", "the", "a", "subtitles by", "captioned by",
    "copyright", "all rights reserved", "", " "
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# ... (rest of binding)

# ... (inside process_audio or main loop logic)
def process_audio():
    # ...
    # After transcription:
    text = result['text'].strip()
    
    # [FIX] Filter Hallucinations
    clean_text = text.lower().strip(".?! ")
    if not clean_text or clean_text in HALLUCINATION_FILTERS:
        print(f"[EARS] Filtered Hallucination: '{text}'")
        return
        
    print(f"[EARS] Heard: '{text}'")
    # ... send to sock ...


# [FIX] Main Socket (Sender & Receiver)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 0)) # [CRITICAL] Bind to receive replies, otherwise recvfrom fails with 10022
sock.setblocking(False)

# [FIX] Command Socket (Listener for MUTE commands)
CMD_PORT = 8009
cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cmd_sock.bind(('0.0.0.0', CMD_PORT))
cmd_sock.setblocking(False)

audio_queue = queue.Queue()
recording_buffer = []
is_recording = False
silence_start = None

def callback(indata, frames, time, status):
    """Called by sounddevice for each audio block."""
    if status:
        print(f"[WARN] {status}")
    audio_queue.put(indata.copy())

def main_loop():
    global is_recording, silence_start, recording_buffer
    mute_until = 0 # [FIX] Initialize local variable
    
    # Start stream
    print(f"\n[EARS] Audio Devices:\n{sd.query_devices()}")
    
    with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, channels=1, callback=callback):
        print(f"\n[EARS] Listening on default mic sending to {HOST_IP}:{HOST_PORT}")
        print("[EARS] Level: [                    ]", end='\r')
        
        while True:
            # 1. Check for incoming replies from SYNZ
            try:
                data, addr = sock.recvfrom(4096)
                reply = data.decode('utf-8')
                if "[AUDIO]" in reply:
                     # Audio Signal (Usually for Unity, but good to know)
                     print(f"\n[SYNZ SIGNAL]: {reply}                     ")
                else:
                     # Text Reply
                     print(f"\n[SYNZ]: {reply}                             ")
                     # Re-print status line
                     print("[EARS] Level: [                    ]", end='\r')
            except BlockingIOError:
                pass # No data
            except Exception as e:
                print(f"\n[ERR] Net: {e}")

            # 2. Check for Commands (Mute/Unmute)
            try:
                data, _ = cmd_sock.recvfrom(1024)
                cmd = data.decode('utf-8').strip()
                if cmd.startswith("MUTE"):
                    duration = float(cmd.split(" ")[1])
                    mute_until = time.time() + duration
                    print(f"\n[EARS] Muted for {duration}s")
                elif cmd == "UNMUTE":
                    mute_until = 0
                    print("\n[EARS] Unmuted.")
            except BlockingIOError:
                pass # No commands
            except Exception:
                pass

            # 3. Check Mute State
            if time.time() < mute_until:
                # Drain audio buffer to prevent backlog while muted
                while not audio_queue.empty():
                    audio_queue.get()
                print(f"\r[EARS] Zzz... ({int(mute_until - time.time())}s)", end="", flush=True)
                time.sleep(0.1) # Small sleep to prevent busy-waiting
                continue

            # 4. Consuming audio chunks
            while not audio_queue.empty():
                chunk = audio_queue.get()
                # Switch to RMS (Root Mean Square) for standard amplitude (0.0 to 1.0)
                # chunk is (4000, 1), flatten it first
                volume = np.sqrt(np.mean(chunk.flatten()**2))
                
                # Visual Meter
                # RMS is usually very small. Noise ~0.001. Speech ~0.1
                bars = int(min(volume * 300, 20)) # Scale up for visibility
                meter = "|" * bars + " " * (20 - bars)
                status = "REC " if is_recording else "    "
                
                # [DEBUG] Show numeric value to help user tune threshold
                print(f"[EARS] Vol:{volume:.4f} |{meter}| {status}", end='\r')
                
                # VAD Logic
                if volume > THRESHOLD:
                    if not is_recording:
                         is_recording = True
                    recording_buffer.append(chunk)
                    silence_start = None # Reset silence timer
                    recording_buffer.append(chunk)
                    silence_start = None # Reset silence timer
                elif is_recording:
                    # We are in a recording session, but this chunk is silent
                    recording_buffer.append(chunk)
                    
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > SILENCE_DURATION:
                         # Silence exceeded limit -> FLUSH
                         # print("\n[EARS] Processing Speech...") 
                         process_audio()
                         
                         # Reset
                         recording_buffer = []
                         is_recording = False
                         silence_start = None
                         # print("[EARS] Listening...")

            time.sleep(0.01)

# --- Wake Word Config ---
WAKE_WORDS = ["SYNZ", "SINS", "SINNS", "SINCE", "SENDS", "XINS", "SCENES", "SYNTH", "SINES", "SIGNS", "SIMS", "SENSE", "CINS", "ZEN", "WAKE UP SYNZ", "WAKE UP SINS", "WAKE UP", "WAKEUP"] # Common Whisper misinterpretations
AWAKE_DURATION = 300.0 # [FIX] 5 Minutes before sleep (User Request)

is_awake = False
last_interaction_time = 0
last_transcription = ""
last_transcription_time = 0

def process_audio():
    """Concatenates buffer and runs Whisper."""
    global is_awake, last_interaction_time, last_transcription, last_transcription_time
    
    if not recording_buffer:
        return

    # Check Sleep Timeout
    if is_awake and (time.time() - last_interaction_time > AWAKE_DURATION):
        print(f"\n[EARS] Timeout ({AWAKE_DURATION}s). Going back to sleep. zzz...")
        is_awake = False

    status_icon = "🟢" if is_awake else "🔴"
    print(f"\n[EARS] Digitizing sequence... {status_icon}        ")

    # Flatten buffer
    audio_data = np.concatenate(recording_buffer, axis=0).flatten()
    
    audio_data = audio_data.astype(np.float32)
    
    # Transcribe
    try:
        # [FIX] condition_on_previous_text=False prevents the "looping" hallucination
        # [UPGRADE] Added initial_prompt to bias towards technical terms and name
        # [SPEED] beam_size=1 (Greedy) is much faster than default (5)
        # [SPEED] temperature=0.0 prevents random sampling loops
        result = model.transcribe(
            audio_data, 
            fp16=False, 
            language="en", 
            beam_size=1, 
            temperature=0.0,
            condition_on_previous_text=False,
            initial_prompt="SYNZ, Unity, C#, programming, AI assistant, wake up"
        ) 
        text = result["text"].strip()
        
        if text:
            # [FIX] Whisper Hallucination Filter
            clean_text = text.lower().strip(".?! ")
            
            # 1. Exact Match Filters (Short common words that appear as ghosts)
            EXACT_FILTERS = {"you", "i", "the", "a", ".", "", " "}
            if clean_text in EXACT_FILTERS:
                print(f"[EARS] Filtered Ghost: '{text}'")
                return

            # 2. Phrase Filters (Artifacts)
            PHRASE_FILTERS = {"thanks for watching", "subtitles by", "captioned by", "copyright", "all rights reserved"}
            if any(p in clean_text for p in PHRASE_FILTERS):
                print(f"[EARS] Filtered Artifact: '{text}'")
                return

        # [FIX] Spam/Loop Block (e.g. "wake up wake up wake up...")
        if len(text) > 256:
             print(f"[EARS] Truncated Spam (Length {len(text)})")
             text = text[:256] # Hard cap

        # Heuristic: If 50% of the string is just one repeated word?
        # Simple check: count "wake up"
        if text.lower().count("wake up") > 3:
             print(f"[EARS] Filtered Loop: '{text}'")
             return # Just drop it.

        if text:
            # [FIX] Deduplication (Debounce)
            # If we hear the EXACT same thing within 2 seconds, it's a double-trigger or echo.
            if text == last_transcription and (time.time() - last_transcription_time) < 2.0:
                print(f"[EARS] Ignored Duplicate: '{text}'")
                return

            last_transcription = text
            last_transcription_time = time.time()

            upper_text = text.upper()
            
            # WAKE WORD CHECK
            if not is_awake:
                detected = any(w in upper_text for w in WAKE_WORDS)
                if detected:
                    print(f"[WAKE] Waking up! Heard: '{text}'")
                    is_awake = True
                    last_interaction_time = time.time()
                    # We pass the wake phrase through so she can respond to "Hey SYNZ what time is it"
                else:
                    print(f"[SLEEPING] Ignored: '{text}' (Say 'WAKE UP' to wake)")
                    return # Ignore this input

            # If we are here, we are AWAKE
            print(f"[HEARD]: {text}")
            last_interaction_time = time.time() # Reset timer
            
            # Send to Face Server
            sock.sendto(text.encode('utf-8'), (HOST_IP, HOST_PORT))
        else:
            print("[EARS] (Heard nothing)")
            
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n[EARS] Stopped.")
