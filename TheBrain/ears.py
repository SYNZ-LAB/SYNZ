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
THRESHOLD = 0.015 
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
                volume = np.linalg.norm(chunk) * 10
                
                # Visual Meter
                bars = int(min(volume * 50, 20))
                meter = "|" * bars + " " * (20 - bars)
                status = "REC " if is_recording else "    "
                print(f"[EARS] {status}[{meter}]", end='\r')
                
                # VAD Logic
                if volume > THRESHOLD:
                    if not is_recording:
                        # print("[EARS] Hearing speech...", end='\r') # Handled by meter now
                        is_recording = True
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

def process_audio():
    """Concatenates buffer and runs Whisper."""
    if not recording_buffer:
        return

    print("\n[EARS] Digitizing sequence...         ")

    # Flatten buffer
    audio_data = np.concatenate(recording_buffer, axis=0).flatten()
    
    # Save DEBUG File
    wav.write("debug_last_heard.wav", SAMPLE_RATE, (audio_data * 32767).astype(np.int16))
    print("[EARS] Saved 'debug_last_heard.wav'")

    audio_data = audio_data.astype(np.float32)
    
    # Transcribe
    try:
        result = model.transcribe(audio_data, fp16=False) # fp16=False for CPU safety
        text = result["text"].strip()
        
        if text:
            print(f"[HEARD]: {text}")
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
