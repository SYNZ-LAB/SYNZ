
import subprocess  # type: ignore
import time  # type: ignore
import os  # type: ignore
import signal  # type: ignore
import sys  # type: ignore
import threading  # type: ignore
from colorama import init, Fore, Style  # type: ignore

init(autoreset=True)

# Config (Fixed for Frozen/EXE)
if getattr(sys, 'frozen', False):
    # Running as EXE
    BASE_DIR = os.path.dirname(sys.executable)
    # If using OneFile, sys.executable is the exe itself.
    # We want to find Client/ folder next to it.
else:
    # Running as Script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = BASE_DIR
DIST_DIR = PROJECT_ROOT # In Release, the launcher IS in the dist dir
UNITY_CLIENT = os.path.join(BASE_DIR, "Client", "SYNZ.exe")

processes = []

def signal_handler(sig, frame):
    print(Fore.YELLOW + "\n[LAUNCHER] Shutting down SYNZ ecosystem...")
    for p in processes:
        p.terminate()
    print(Fore.GREEN + "[DONE] Bye!")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def launch_exe(name, exe_name, args=[]):
    """Launches an EXE from dist/ folder or falls back to Python script."""
    # Try resolving path (Support OneDir structure)
    exe_path = os.path.join(DIST_DIR, exe_name)
    if not os.path.exists(exe_path):
        # Try subdirectory (e.g. dist/SYNZ_Backend/brain/brain.exe)
        folder_name = exe_name.replace(".exe", "")
        exe_path = os.path.join(DIST_DIR, folder_name, exe_name)

    script_path = os.path.join(PROJECT_ROOT, "TheBrain", exe_name.replace(".exe", "_server.py"))
    if exe_name == "ears.exe":
        script_path = os.path.join(PROJECT_ROOT, "TheBrain", "ears.py")

    cmd = []
    if os.path.exists(exe_path):
        print(f"{Fore.CYAN}[LAUNCH] Starting {name} (Compiled)...")
        # [DEBUG] Use cmd /k to keep window open on crash
        cmd = ["cmd", "/k", exe_path] + args
    elif os.path.exists(script_path):
        print(f"{Fore.BLUE}[DEV] Starting {name} (Script)...")
        cmd = ["cmd", "/k", sys.executable, script_path] + args
    else:
        print(f"{Fore.RED}[ERR] Could not find {name} at {exe_path} or {script_path}")
        return

    # Launch
    # creationflags=subprocess.CREATE_NEW_CONSOLE (Open new window)
    # OR capture output?
    # For release, user probably wants ONE window.
    # But for debugging, new windows are better.
    # Let's use NEW_CONSOLE for now so they can see logs if needed.
    # If they want silent, we'd use piped stdout.
    
    p = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    processes.append(p)

def main():
    print(Fore.MAGENTA + "="*40)
    print(Fore.MAGENTA + "       SYNZ: NEURO-LINK LAUNCHER")
    print(Fore.MAGENTA + "="*40)
    
    # 1. Start Servers
    launch_exe("Brain (Logic)", "brain.exe")
    time.sleep(2) # Wait for Llama load
    
    launch_exe("Ears (Senses)", "ears.exe")
    launch_exe("Face (Router)", "face.exe")
    
    # 2. Start Unity (if built)
    if os.path.exists(UNITY_CLIENT):
        print(f"{Fore.GREEN}[UNITY] Launching Client...")
        # [FIX] Force Resolution to prevent invisible 1x1 window bug
        unity_args = [
            "-screen-width", "1920", 
            "-screen-height", "1080",
            "-popupwindow" # Borderless
        ]
        p = subprocess.Popen([UNITY_CLIENT] + unity_args, cwd=os.path.dirname(UNITY_CLIENT))
        processes.append(p)
    else:
        print(f"{Fore.YELLOW}[WARN] Unity Client not found at {UNITY_CLIENT}")
        print("      (Build Unity project to 'Client/' folder to enable auto-launch)")

    print(Fore.GREEN + "\n[SYSTEM] SYNZ is Active. Press Ctrl+C to Shutdown.")
    
    # Monitor loop
    try:
        while True:
            time.sleep(1)
            # Check if processes died?
            dead = [p for p in processes if p.poll() is not None]
            if dead:
                # If everything died, exit
                if len(dead) == len(processes):
                    print("[EXIT] All systems offline.")
                    break
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
