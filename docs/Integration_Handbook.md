# 🧩 SYNZ Integration Handbook

This guide covers the 3 critical systems to complete the "Dual-Brain" architecture.

---

## 1. 💃 The Body (Unity + Live2D)
**Goal**: Make the Live2D model smile when the Brain says `<HAPPY>`.

### Step A: Update `NeuroLinkClient.cs`
We need to parse the tags *before* showing the text bubble.

```csharp
// Inside OnMessageReceived(string message)
string cleanMessage = message;
string emotion = "NORMAL";

if (message.Contains("<HAPPY>")) {
    emotion = "HAPPY";
    cleanMessage = message.Replace("<HAPPY>", "");
}
else if (message.Contains("<ANGRY>")) {
    emotion = "ANGRY";
    cleanMessage = message.Replace("<ANGRY>", "");
}

// 1. Show Clean Text
uiText.text = cleanMessage;

// 2. Trigger Body
var controller = FindObjectOfType<CubismSYNZController>();
if (controller != null) {
    controller.SetEmotion(emotion);
    controller.SetTalking(true);
    // (Remember to set Talking = false after a delay!)
}
```

---

## 2. 🌉 The Bridge (C++ <-> Python)
**Goal**: The C++ Core sends a "Prompt" to Python, Python replies.

### Step A: `TheBrain/face_server.py`
Run this script to host the brain.

```python
import socket
from model import NanoSYNZ
# ... Load Model ...

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 8005)) # Listen on 8005

print("[FACE] Listening for thoughts...")
while True:
    data, addr = sock.recvfrom(1024)
    prompt = data.decode('utf-8')
    
    # 1. Run Brain (Generate)
    reply = generate_reply(model, prompt) 
    
    # 2. Send Back
    sock.sendto(reply.encode('utf-8'), addr)
```

### Step B: C++ Client (`src/LlamaEngine.h`)
Update the C++ engine to forward non-code questions to port 8005.

```cpp
// If query is "Chat", send to Python
if (isChat) {
    UDPSocket sock;
    sock.send("127.0.0.1", 8005, input);
    return sock.receive(); // Returns "Hi! <HAPPY>"
}
```

---

## 3. 💉 The Data Pipeline (Discord)
**Goal**: Ingest real human conversation logs.
> [!NOTE]
> **Assignment**: This task is assigned to **Jeremy / Xykoss**.
> *"Good luck filtering out the memes."*

### Specification
Create `TheBrain/import_discord.py`.

1.  **Input**: A `.csv` or `.json` file from **DiscordChatExporter**.
2.  **Logic**:
    *   Filter by User ID (Only keep *your* messages).
    *   Remove URLs (Links confuse the small brain).
    *   Remove custom emotes (`:peepoHappy:` -> clean text).
3.  **Output**: Overwrite `TheBrain/personality_data.json` with the clean list.

```python
# Pseudo-code for Jeremy
import pandas as pd

df = pd.read_csv("discord_logs.csv")
my_msgs = df[df['AuthorID'] == YOUR_ID]['Content']

clean_data = [{"text": msg} for msg in my_msgs if isinstance(msg, str)]

# Save to JSON
```
