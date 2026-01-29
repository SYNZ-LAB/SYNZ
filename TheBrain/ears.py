import sounddevice as sd
import numpy as np
import whisper
import socket
import time
import queue
import scipy.io.wavfile as wav

# --- Configuration ---
HOST_IP = "127.0.0.1"
HOST_PORT = 8005
SAMPLE_RATE = 16000
BLOCK_SIZE = 4000 
THRESHOLD = 0.02 # RMS Threshold (Silence is usually < 0.01)
SILENCE_DURATION = 0.6 # Reduced from 1.0 for snappier response

print("[EARS] Loading Model 'tiny' for speed... (This may take a moment)")
model = whisper.load_model("tiny") # Switched from 'base' to 'tiny'
print("[EARS] Model Loaded. Listening...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 0)) # Bind to ephemeral port to receive replies
sock.setblocking(False) # Enable non-blocking mode for listening

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

            # 2. Consuming audio chunks
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
AWAKE_DURATION = 30.0 # How long to stay awake after last interaction

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
        result = model.transcribe(audio_data, fp16=False, language="en", condition_on_previous_text=False) 
        text = result["text"].strip()
        
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
