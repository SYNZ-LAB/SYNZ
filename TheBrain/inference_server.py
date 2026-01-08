import socket
import json
import torch
from model import LilithConfig, LilithModel
from tokenizer import get_tokenizer
from personality import PersonalityManager

# Configuration
WATCHER_PORT = 5005 # Receives from The Watcher
BODY_PORT = 5006    # Sends to The Body (Unity)
MODEL_PATH = "lilith_model.pt"
TOKENIZER_PATH = "lilith_tokenizer.json"

def load_brain():
    # Load tokenizer
    tokenizer = get_tokenizer(TOKENIZER_PATH)
    
    # Load model
    config = LilithConfig()
    config.vocab_size = tokenizer.get_vocab_size()
    # Use small config for local inference efficiency
    config.n_layer = 4
    config.n_head = 4
    config.n_embd = 128
    config.block_size = 64
    
    model = LilithModel(config)
    if torch.cuda.is_available():
        model.to('cuda')
    
    # Try to load weights if they exist
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu', weights_only=True))
        print(f"Loaded model weights from {MODEL_PATH}")
    except Exception as e:
        print(f"Failed to load model weights: {e}")
        print("Running with random initialization for testing.")
    
    model.eval()
    return model, tokenizer

def generate_response(model, tokenizer, personality, input_text):
    # CLUE #3: Use the personality manager to wrap the input
    processed_input = personality.process_input(input_text)
    
    tokens = tokenizer.encode(processed_input).ids
    idx = torch.tensor([tokens], dtype=torch.long)
    if torch.cuda.is_available():
        idx = idx.to('cuda')
        
    with torch.no_grad():
        logits, _ = model(idx)
        # Get the most likely next token
        probs = torch.softmax(logits[:, -1, :], dim=-1)
        next_token = torch.argmax(probs, dim=-1).item()
        
    response_token = tokenizer.id_to_token(next_token)
    
    # Map token to action
    action = "NEUTRAL"
    if "<ACTION_SURPRISE>" in response_token: action = "SURPRISE"
    elif "<ACTION_SMILE>" in response_token: action = "SMILE"
    elif "<ACTION_THINK>" in response_token: action = "THINK"
    
    # CLUE #4: Let personality filter or modify the action
    final_action = personality.process_output(action)
    
    return final_action

def start_server():
    model, tokenizer = load_brain()
    personality = PersonalityManager()
    
    # Setup UDP sockets
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind(("127.0.0.1", WATCHER_PORT))
    
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"The Brain is listening on port {WATCHER_PORT}...")
    
    while True:
        data, addr = recv_sock.recvfrom(1024)
        try:
            msg = json.loads(data.decode('utf-8'))
            print(f"Received from Watcher: {msg}")
            
            if msg.get("type") == "error":
                # Process error and decide on action
                error_content = msg.get("content", "")
                action = generate_response(model, tokenizer, personality, error_content)
                
                # Send to Body
                response = json.dumps({"action": action})
                send_sock.sendto(response.encode('utf-8'), ("127.0.0.1", BODY_PORT))
                print(f"Sent to Body: {response}")
                
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    start_server()
