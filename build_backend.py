
import os  # type: ignore
import sys  # type: ignore
import shutil  # type: ignore
import subprocess  # type: ignore
import PyInstaller.__main__  # type: ignore

# Config
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BRAIN_DIR = os.path.join(PROJECT_ROOT, "TheBrain")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist", "SYNZ_Backend")

def build_exe(script_name, script_path, hidden_imports=[]):
    print(f"\n[BUILD] Building {script_name}...")
    
    args = [
        script_path,
        '--onedir', # [FIX] OneDir prevents unpacking extraction errors (WinError -3)
        '--name', script_name,
        '--distpath', DIST_DIR,
        '--workpath', os.path.join(PROJECT_ROOT, "build", "temp"),
        '--specpath', os.path.join(PROJECT_ROOT, "build", "specs"),
        '--clean',
        '--log-level', 'WARN',
        # Optimizations
        # '--noupx', # Disable UPX if it causes issues
    ]
    
    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')

    # Special handling for Whisper/Torch/Llama
    args.append('--collect-all=whisper')
    args.append('--collect-all=torch')
    args.append('--collect-all=llama_cpp') # Module Name
    args.append('--collect-all=llama_cpp_python') # Package Name
    
    PyInstaller.__main__.run(args)
    print(f"[SUCCESS] Built {script_name}.exe")

def main():
    # 0. Clean (Smart)
    # Don't wipe 'Client' folder if it exists
    os.makedirs(DIST_DIR, exist_ok=True)
    for item in ["brain", "face", "ears", "brain.exe", "face.exe", "ears.exe", "models", "data"]:
        path = os.path.join(DIST_DIR, item)
        if os.path.exists(path):
            try:
                if os.path.isdir(path): shutil.rmtree(path)
                else: os.remove(path)
            except: pass

    # 1. Build Servers
    # Ears: Needs whisper, sounddevice, winsound
    build_exe("ears", os.path.join(BRAIN_DIR, "ears.py"), 
             hidden_imports=['sounddevice', 'numpy', 'scipy.io.wavfile', 'whisper'])

    # Brain: Needs llama-cpp-python, colorama, win32pipe
    build_exe("brain", os.path.join(BRAIN_DIR, "brain_server.py"),
             hidden_imports=['llama_cpp', 'colorama', 'win32pipe', 'win32file'])

    # Face: Needs torch, duckduckgo_search, colorama, etc.
    build_exe("face", os.path.join(BRAIN_DIR, "face_server.py"),
             hidden_imports=['torch', 'duckduckgo_search', 'colorama', 'socket', 're'])

    # 2. Copy Assets
    print("\n[ASSETS] Copying resources...")
    
    # Models Folder
    src_models = os.path.join(PROJECT_ROOT, "models")
    dst_models = os.path.join(DIST_DIR, "models")
    if os.path.exists(src_models):
        shutil.copytree(src_models, dst_models)
        print(f"Copied models -> {dst_models}")
    else:
        print("[WARN] No 'models' folder found in project root. You must populate it manually.")
        os.makedirs(dst_models, exist_ok=True)

    # Brain Assets
    assets = ["synz_face.pth", "meta.pkl", "response.mp3"]
    for asset in assets:
        src = os.path.join(BRAIN_DIR, asset)
        if os.path.exists(src):
            shutil.copy(src, DIST_DIR)
            print(f"Copied {asset}")

    # Data Folder (Memory)
    src_data = os.path.join(BRAIN_DIR, "data")
    dst_data = os.path.join(DIST_DIR, "data")
    if os.path.exists(src_data):
        shutil.copytree(src_data, dst_data)
        print("Copied data/ folder")

    print("\n[DONE] Distribution build complete in dist/SYNZ_Backend")

if __name__ == "__main__":
    # Check for PyInstaller
    try:
        import PyInstaller  # type: ignore
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    main()
