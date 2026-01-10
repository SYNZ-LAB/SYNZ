#include "Sentinel.h" // Import our new Agent Class
#include <iostream>

int main() {
    std::cout << "BOOTING SYSTEM..." << std::endl;
    std::cout << "Initializing SYNZ Sentinel (Phase 2)..." << std::endl;

    // == CONFIGURATION ==
    // Unity's default Editor.log location
    std::string logDir = "C:\\Users\\Adminb\\AppData\\Local\\Unity\\Editor";
    std::string targetFile = "Editor.log";
    
    // The Brain's address (Localhost)
    std::string brainIp = "127.0.0.1";
    int brainPort = 5005;

    // == SPAWN SENTINEL ==
    // Creates the instance with our config
    Sentinel sentinel(logDir, targetFile, brainIp, brainPort);
    
    // == START AGENT ==
    // Enters the infinite watch loop
    sentinel.start();

    return 0;
}
