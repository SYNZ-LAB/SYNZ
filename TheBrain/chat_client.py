import socket
import sys
import time

HOST_IP = "127.0.0.1"
HOST_PORT = 8005

def chat_loop():
    print("==========================================")
    print("       SYNZ TERMINAL UPLINK ACTIVE        ")
    print("==========================================")
    print("commands: !good (Reinforce), !bad (Discard)")
    print("Ctrl+C to exit.")
    print("------------------------------------------")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(15.0) # Generous timeout for TTS

    while True:
        try:
            user_input = input("\n[YOU]: ").strip()
            if not user_input:
                continue

            # Send
            sock.sendto(user_input.encode('utf-8'), (HOST_IP, HOST_PORT))

            # Receive
            data, addr = sock.recvfrom(4096)
            reply = data.decode('utf-8')
            
            print(f"[SYNZ]: {reply}")
            
            # Since we know the server generates a file, we can mention it
            if "response.mp3" in reply or True: # Always mentioning for now
                print("       (Audio file updated: response.mp3)")

        except KeyboardInterrupt:
            print("\n[SYSTEM] Uplink closed. Bye.")
            break
        except socket.timeout:
            print("[SYSTEM] No response. (Is the server generating audio? Wait...)")
        except ConnectionResetError:
             print("\n[ERROR] Connection Reset! Server is OFFLINE.")
             print("[HINT] Did you start 'face_server.py' in the other window?")
             # We don't break, maybe they restart the server
             time.sleep(1)
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    chat_loop()
