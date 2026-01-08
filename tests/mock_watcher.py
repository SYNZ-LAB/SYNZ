import socket
import json
import time

BRAIN_PORT = 5005

def send_error(error_msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = json.dumps({"type": "error", "content": error_msg})
    sock.sendto(msg.encode('utf-8'), ("127.0.0.1", BRAIN_PORT))
    print(f"Sent error to Brain: {error_msg}")

if __name__ == "__main__":
    time.sleep(2) # Wait for brain to start
    send_error("NullReferenceException: Object reference not set to an instance of an object")
    time.sleep(1)
    send_error("Error: Shader compilation failed")
