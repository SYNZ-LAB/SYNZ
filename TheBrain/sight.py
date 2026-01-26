import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import mss
import mss.tools
import os
import time

class SightAgent:
    def __init__(self):
        print("[SIGHT] Initializing Visual Cortex (Moondream2)...")
        # Use Moondream2 (Small VLM)
        self.model_id = "vikhyatk/moondream2"
        self.revision = "2024-08-26" # Pin revision for stability
        
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id, 
                trust_remote_code=True, 
                revision=self.revision
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, revision=self.revision)
            
            # Check GPU availability (Moondream works okay on CPU too, but GPU is better)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            self.model.eval()
            print(f"[SIGHT] Eyes Opened on {self.device}.")
        except Exception as e:
            print(f"[ERR] Vision Init Failed: {e}")
            self.model = None

    def capture_screen(self):
        """Takes a screenshot of the primary monitor."""
        with mss.mss() as sct:
            monitor = sct.monitors[1] # Primary monitor
            sct_img = sct.grab(monitor)
            # Convert to PIL Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return img

    def analyze(self, query="Describe this image."):
        """Looks at screen and answers query."""
        if not self.model:
            return "I am blind. (Model load failed)"

        try:
            image = self.capture_screen()
            
            # Encode
            enc_image = self.model.encode_image(image)
            
            # Generate
            answer = self.model.answer_question(enc_image, query, self.tokenizer)
            
            return f"[VISUAL ANALYSIS]: {answer}"
        except Exception as e:
            return f"[BLINDED]: {e}"

if __name__ == "__main__":
    # Test
    eye = SightAgent()
    print(eye.analyze("What is on the screen right now?"))
