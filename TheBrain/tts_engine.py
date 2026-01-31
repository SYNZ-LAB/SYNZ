import asyncio
import edge_tts
import sys
import warnings

# [FIX] Suppress the asyncio warning on Windows
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Voice Options:
# en-US-AnaNeural (Child-like)
# en-US-JennyNeural (Adult Assistant)
# en-AU-NatashaNeural (Australian Female) [SELECTED]
# en-AU-WilliamNeural (Australian Male)
VOICE = "en-AU-NatashaNeural" 
OUTPUT_FILE = "test_audio.mp3"

async def generate_voice(text, filename):
    print(f"[TTS] Generating: '{text}' using {VOICE}")
    # Pitch +15Hz makes it sound slightly younger (Teen)
    communicate = edge_tts.Communicate(text, VOICE, rate="+0%", pitch="+15Hz") 
    await communicate.save(filename)
    print(f"[TTS] Saved to {filename}")

    print(f"[TTS] Saved to {filename}")

def generate_audio_sync(text, filename):
    """Synchronous wrapper for Face Server."""
    try:
        if sys.platform == "win32":
            # Policy fix for Windows
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
        asyncio.run(generate_voice(text, filename))
        return True
    except Exception as e:
        print(f"[TTS ERROR] {e}")
        return False

if __name__ == "__main__":
    text = "It's not like I wanted you to install me or anything! Baka!"
    if len(sys.argv) > 1:
        text = sys.argv[1]
        
    generate_audio_sync(text, OUTPUT_FILE)
