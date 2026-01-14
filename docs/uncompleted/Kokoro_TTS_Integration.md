# 🗣️ Kokoro TTS Integration Guide

**Goal**: Give SYNZ a high-quality, anime-style voice using **Kokoro** (or StyleTTS2).
**Status**: Planned (Uncompleted).

## 1. The Architecture
TTS is heavy. It cannot run inside the main C++ Core. It must live in `face_server.py` (The Python Face).

*   **Input**: Text from NanoSYNZ ("I-It's not like I like you! <TSUN>").
*   **Process**:
    1.  Clean text (remove `<TAGS>`).
    2.  Pass to Kokoro Model.
    3.  Generate `.wav` bytes.
    4.  Send Audio Bytes -> C++ Core -> NeuroLink -> Unity.
*   **Output**: Unity plays the audio.

## 2. Requirements
Add these to `TheBrain/requirements.txt`:
```text
kokoro>=0.3.0
soundfile
numpy
scipy
torch
```
(Note: Kokoro requires `espeak-ng` installed on the system).

## 3. Implementation Plan (`face_server.py`)

```python
from kokoro import KPipeline
import soundfile as sf
import io

# Initialize
pipeline = KPipeline(lang_code='a') # 'a' for American English
voice = 'af_bella' # Cute female voice

def generate_voice(text):
    # 1. Generate Audio
    generator = pipeline(text, voice=voice, speed=1.0)
    
    # 2. Setup Buffer
    audio_buffer = io.BytesIO()
    
    # 3. Stream/Save
    for i, (gs, ps, audio) in enumerate(generator):
        sf.write(audio_buffer, audio, 24000, format='WAV')
        break # Just first segment for low latency test
        
    return audio_buffer.getvalue()
```

## 4. The Unity Problem
Unity handles Audio Streams differently than Text.
*   **Current Pipe**: Sends JSON Strings.
*   **New Pipe Needed**: A separate Named Pipe `\\.\pipe\synz_audio` OR embed Base64 encoded audio in the JSON (slower but easier).

**Recommendation**: Use Base64 inside JSON for the prototype.
`{ "type": "audio", "data": "UklGRi..." }`
