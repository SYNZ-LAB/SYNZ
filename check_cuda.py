
import torch  # type: ignore
import sys  # type: ignore
try:
    from llama_cpp import Llama  # type: ignore
    HAS_LLAMA = True
except ImportError:
    HAS_LLAMA = False

print(f"Python: {sys.version}")
print(f"Torch Version: {torch.__version__}")
print(f"CUDA Available (Torch): {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA Device: None")

if HAS_LLAMA:
    print("Llama-cpp-python: Installed")
    # We can't easily check compiled flags without trying to load, 
    # but we can infer from package metadata or just trying to load dummy.
else:
    print("Llama-cpp-python: Not Installed")
