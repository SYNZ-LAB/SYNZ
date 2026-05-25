import socket  # type: ignore
import time  # type: ignore
import os  # type: ignore
import threading  # type: ignore

# Configuration
FACE_IP = "127.0.0.1"
FACE_PORT = 8005

# Setup Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 0)) # Bind to any free port
sock.setblocking(True)

print(f"--- SYNZ Voice Chat Tester ---")
print(f"Target: {FACE_IP}:{FACE_PORT}")
print(f"My Address: {sock.getsockname()}")
print("Type a message and press Enter. SYNZ should reply in Voice.")
print("----------------------------------------------------------")

def listen_loop():
    while True:
        try:
            data, addr = sock.recvfrom(65535)
            msg = data.decode('utf-8')
            
            if msg.startswith("[AUDIO]"):
                audio_path = msg[7:].strip()
                print(f"\n[RECEIVED AUDIO]: {audio_path}")
                if os.path.exists(audio_path):
                    print(f"Playing audio...")
                    # Windows: Use PowerShell to play sound without opening a window/player, 
                    # OR just open it. os.startfile opens default player (Groove/Media Player).
                    # A quieter way is using powershell.
                    cmd = f'powershell -c (New-Object Media.SoundPlayer "{audio_path}").PlaySync();'
                    # But SoundPlayer only supports WAV. We have MP3.
                    # Fallback: os.startfile (It pops up, but it works).
                    # OR just telling user "Audio Generated".
                    # Let's try os.startfile for now, user can hear it.
                    try:
                        os.startfile(audio_path)
                    except Exception as e:
                        print(f"Could not auto-play: {e}")
            else:
                print(f"\n[SYNZ]: {msg}")
                print("\nYou: ", end="", flush=True)
                
        except ConnectionResetError:
            print("[Error] Connection Reset by Remote Host.")
        except Exception as e:
            print(f"[Error] {e}")

# Start Listener in Background
t = threading.Thread(target=listen_loop, daemon=True)
t.start()

# Main Input Loop
try:
    while True:
        text = input("You: ")
        if text.lower() == "exit":
            break
        if text.strip() == "":
            continue
            
        # Send to Face Server
        print(f"[Sending] '{text}'...")
        sock.sendto(text.encode('utf-8'), (FACE_IP, FACE_PORT))
        
        # Adding a sleep to prevent prompt overlap visually
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting...")
