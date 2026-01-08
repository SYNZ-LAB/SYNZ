import socket
import json

BODY_PORT = 5006

def start_mock_body():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", BODY_PORT))
    print(f"Mock Body listening on port {BODY_PORT}...")
    
    while True:
        data, addr = sock.recvfrom(1024)
        msg = json.loads(data.decode('utf-8'))
        print(f"Received action from Brain: {msg}")

if __name__ == "__main__":
    start_mock_body()
