import socket
import json
import time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005

def send_test_packet():
    print(f"Test Sender: Sending packet to {SERVER_IP}:{SERVER_PORT}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Simulate the Sentinel's payload
    # Note: We send 5 lines of context
    context = (
        "void Update() {\n"
        "   if (target == null) {\n"
        "       // Oops logic error\n"
        "       float x = 0;\n"
        "       Debug.Log(x);\n"
    )
    
    payload = {
        "type": "error",
        "error_type": "NullReference",
        "content": context + "NullReferenceException: Object reference not set to an instance of an object"
    }
    
    message = json.dumps(payload).encode('utf-8')
    
    try:
        sock.sendto(message, (SERVER_IP, SERVER_PORT))
        print("Test Sender: Packet Sent!")
    except Exception as e:
        print(f"Test Sender: Error - {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    # Give the brain a second to breathe if started simultaneously
    time.sleep(1)
    send_test_packet()
