import sounddevice as sd
import numpy as np
import whisper
import socket
import time
import os

# Configuration
FACE_IP = "127.0.0.1"
FACE_PORT = 8005
SAMPLE_RATE = 16000
DURATION = 5 # Record for 5 seconds

print("[TEST_MIC] Initializing...")
print("[TEST_MIC] Loading Whisper Model (This connects the ear to the brain)...")
try:
    model = whisper.load_model("tiny")
    print("[TEST_MIC] Model Loaded.")
except Exception as e:
    print(f"[ERR] Whisper Load Failed: {e}")
    exit()

def record_audio(seconds):
    print(f"\n[TEST_MIC] 🎙️ RECORDING for {seconds} seconds... SPEAK NOW!")
    print("[TEST_MIC] (Say 'Hello SYNZ' clearly)")
    
    # Record
    myrecording = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()  # Wait until recording is finished
    print("[TEST_MIC] ⏹️ Recording Stopped.")
    return myrecording.flatten()

def transcribe(audio_data):
    print("[TEST_MIC] Transcribing...")
    audio_data = audio_data.astype(np.float32)
    result = model.transcribe(audio_data, fp16=False)
    text = result["text"].strip()
    return text

def send_to_brain(text):
    if not text:
        print("[TEST_MIC] Heard silence. Aborting network test.")
        return

    print(f"[TEST_MIC] Heard: '{text}'")
    print(f"[TEST_MIC] Sending to Face Server ({FACE_PORT})...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10.0)
    
    try:
        sock.sendto(text.encode('utf-8'), (FACE_IP, FACE_PORT))
        
        print("[TEST_MIC] Waiting for reply...")
        data, addr = sock.recvfrom(65535)
        reply = data.decode('utf-8')
        print(f"\n[TEST_MIC] 🧠 RESPONSE: {reply}")
        
    except socket.timeout:
        print("[TEST_MIC] [ERR] Timed out waiting for SYNZ. Is start_synz.bat running?")
    except Exception as e:
        print(f"[TEST_MIC] [ERR] Network error: {e}")

if __name__ == "__main__":
    audio = record_audio(DURATION)
    text = transcribe(audio)
    print(f"\n[TEST_MIC] 📝 TRANSCRIPTION: {text}")
    send_to_brain(text)
    print("\n[TEST_MIC] Test Complete.")
