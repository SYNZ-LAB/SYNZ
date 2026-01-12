import requests
import json
import threading

# Configuration for Local LLM (Ollama)
OLLAMA_URL = "http://localhost:11434/api/generate"
# DeepSeek Coder is currently the best "Gemini-level" open model
MODEL_NAME = "deepseek-coder-v2" 

class DeepBrain:
    def __init__(self):
        self.thinking = False

    def analyze_error_async(self, context_lines, error_message, callback):
        """
        Starts a background thread to ask the LLM for help without blocking the main thread.
        "Realtime" feel comes from non-blocking UI + Async processing.
        """
        thread = threading.Thread(target=self._query_ollama, args=(context_lines, error_message, callback))
        thread.start()

    def _query_ollama(self, context, error, callback):
        self.thinking = True
        
        prompt = f"""
        You are an expert AI coding assistant.
        Analyze the following code context and error.
        
        CONTEXT:
        {context}
        
        ERROR:
        {error}
        
        Provide a concise, 1-sentence explanation of what is wrong, followed by the fixed line of code.
        Do not explain 'why' excessively, just fix it.
        """
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            # This request might take 2-5 seconds locally
            response = requests.post(OLLAMA_URL, json=payload)
            result = response.json().get("response", "")
            
            # Send the smart result back to the Body
            callback(result)
            
        except Exception as e:
            print(f"[DeepBrain] Error: {e}")
        finally:
            self.thinking = False

# Example Usage Mock
if __name__ == "__main__":
    def print_fix(fix):
        print(f"\\n[Lilith]: {fix}")

    brain = DeepBrain()
    print("[System] Error detected. Creating reaction... (Fast Brain)")
    print("[System] Consulting Deep Brain...")
    
    # Mock Context
    ctx = "float x = 0;\\nDebug.Log(x.ToString());"
    err = "NullReferenceException"
    
    brain.analyze_error_async(ctx, err, print_fix)
    print("[System] Main thread continues (Lilith is smiling/waiting)...")
