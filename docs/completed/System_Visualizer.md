# 🧠 SYNZ System Schematic (The Dual-Brain)

This document visualizes how the different organs of SYNZ communicate.

## The Wiring Diagram

```mermaid
graph TD
    %% Nodes
    User[USER (You)]
    
    subgraph "THE BODY (Unity Editor)"
        Unity[Unity c# Scripts]
        NeuroLink[NeuroLinkClient.cs]
        Live2D[Live2D Cubism Controller]
    end

    subgraph "THE LEFT BRAIN (Logic)"
        CoreWin[main.cpp (Windows Loop)]
        LLM[Qwen 2.5 (C++ LlamaEngine)]
        Monitor[CodeMonitor.h]
        PipeServ[NeuroLink.h (Named Pipe Server)]
    end

    subgraph "THE RIGHT BRAIN (Personality)"
        FaceServ[face_server.py (UDP Server)]
        SLM[NanoSYNZ (Python Model)]
    end

    %% Connections
    
    %% Input Flow
    User -->|Voice/Chat| NeuroLink
    NeuroLink -->|Raw Data| FaceServ
    
    %% The Controller (SLM)
    FaceServ -->|Prompt| SLM
    SLM -- "Is this code?" --> Router{Router}
    
    %% Branch A: Social
    Router -- No --> ResponseGen[Generate Social Reply]
    
    %% Branch B: Logic
    Router -- Yes --> UDP[UDP Request]
    UDP -->|Code Query| CoreWin
    CoreWin -->|Inference| LLM
    LLM -->|Solution| CoreWin
    CoreWin -->|Code Result| UDP
    UDP -->|Raw Code| FaceServ
    FaceServ -->|Add Sass/Personality| ResponseGen
    
    %% The Sentinel (Proactive)
    Monitor -->|Detect Error| CoreWin
    CoreWin -->|Alert| FaceServ
    FaceServ -->|Generate Scolding| ResponseGen
    
    %% Output
    ResponseGen -->|Reply + Tags| NeuroLink
    NeuroLink -->|TTS & Animation| User
```

## The Protocols

### 1. The Spinal Cord (Unity <-> C++ Core)
*   **Protocol**: **Named Pipes** (`\\.\pipe\synz_link`).
*   **Why**: Extremely fast, reliable, standard on Windows. It's like a direct physical cable between Unity and the Background Process.
*   **Data**: JSON strings (`{"type": "chat", "msg": "hello"}`).

### 2. The Corpus Callosum (C++ Core <-> Python Face)
*   **Protocol**: **UDP Sockets** (`localhost:8005`).
*   **Why**: 
    *   **Decoupled**: The C++ Core doesn't care if Python crashes or restarts.
    *   **Fast**: Fire-and-forget packets.
    *   **Simple**: C++ sends "Context", Python replies "Personality".
*   **Data**: Raw UTF-8 Text.

## The "Thought Process" (Example)
1.  **You** say "Good morning" in Unity.
2.  **Unity** sends JSON to C++ Core via Pipe.
3.  **C++ Core** decides: "This is a chat, not a code error."
4.  **C++ Core** forwards "Good morning" to Python via UDP.
5.  **Python (SLM)** generates: "Morning! Coffee yet? <HAPPY>"
6.  **Python** sends reply back to C++ via UDP.
7.  **C++ Core** forwards reply to Unity via Pipe.
8.  **Unity** shows text "Morning! Coffee yet?" and triggers **Live2D** `<HAPPY>`.
