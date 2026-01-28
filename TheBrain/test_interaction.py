import socket
import time
import threading

# Configuration
FACE_IP = "127.0.0.1"
FACE_PORT = 8005

# Create a socket to act as the "User"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(10.0) # Wait up to 10 seconds for a brain response

def listen():
    print("[TEST] Listening for SYNZ response...")
    start = time.time()
    while time.time() - start < 10:
        try:
            data, addr = sock.recvfrom(4096)
            msg = data.decode('utf-8')
            print(f"[TEST] RECEIVED: {msg}")
            if "[AUDIO]" in msg:
                print("[TEST] SUCCESS: Audio Signal Detected!")
                return
        except socket.timeout:
            break
        except Exception as e:
            print(f"[TEST] Error: {e}")
            break
    print("[TEST] Finished listening.")

# Start Listener Thread
t = threading.Thread(target=listen)
t.start()

# Send Message
msg = "Hello SYNZ, introduce yourself."
print(f"[TEST] Sending: '{msg}' to {FACE_PORT}...")
sock.sendto(msg.encode('utf-8'), (FACE_IP, FACE_PORT))

# Wait
t.join()
print("[TEST] Test Complete.")
