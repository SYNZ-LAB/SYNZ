import socket
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 8005
MESSAGE = sys.argv[1] if len(sys.argv) > 1 else "Hello from Test Script"

print(f"UDP target IP: {UDP_IP}")
print(f"UDP target port: {UDP_PORT}")
print(f"message: {MESSAGE}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(10.0) # Wait up to 10s for TTS
sock.sendto(bytes(MESSAGE, "utf-8"), (UDP_IP, UDP_PORT))

print("[TEST] Message sent. Waiting for reply (up to 10s)...")
try:
    data, addr = sock.recvfrom(4096)
    print(f"[REPLY]: {data.decode('utf-8')}")
except socket.timeout:
    print("[ERROR] Timed out waiting for reply! (Is server crashing or TTS too slow?)")
except Exception as e:
    print(f"[ERROR] {e}")
