#define WIN32_LEAN_AND_MEAN
#include "LlamaEngine.h"
#include "NeuroLink.h"
#include "LogMonitor.h"
#include "CodeMonitor.h"
#include "UDPServer.h"
#include <thread>

int main(){
    std::cout << "BOOTING SYNZ CORE (Native Architecture)..." << std::endl;
    
    NeuroLink link;
    LlamaEngine brain; 
    UDPServer udp_bridge(8006); // The Logic Bridge

    // Initialize Brain
    // Initialize Brain (Llama 3 8B - GPU Mode)
    std::string model_path = "models/Llama-3.1-8B-Instruct-Q6_K.gguf";
    brain.load_model(model_path); 

    // Initialize Eyes (Log Watcher)
    std::string log_path = "C:/Users/Adminb/AppData/Local/Unity/Editor/Editor.log";
    LogMonitor bot_eye(log_path);
    
    // Initialize Sentinel (Code Watcher) - Pointing to unity_scripts for now
    std::string code_path = "c:/Users/Adminb/OneDrive/Documents/Projects/SYNZ/unity_scripts";
    CodeMonitor sentinel(code_path);

    std::cout << "[SYNZ] Watching Logs: " << log_path << std::endl;
    std::cout << "[SYNZ] Watching Code: " << code_path << std::endl;
    std::cout << "[SYNZ] Logic Bridge Open on Port 8006" << std::endl;

    while (true) {
        // 1. Check Logs
        std::string new_logs = bot_eye.check();
        if (!new_logs.empty()) {
            std::cout << "\n[DETECTED LOG]: " << new_logs << std::endl;
            if (new_logs.find("Exception") != std::string::npos || 
                new_logs.find("Error") != std::string::npos) {
                
                std::cout << "[SYNZ] Thinking..." << std::endl;
                std::string fix = brain.infer("System Error:\n" + new_logs);
                link.send_reaction(fix);
            }
        }

        // 2. Check Code
        std::string new_code = sentinel.check();
        if (!new_code.empty()) {
             std::cout << "\n[DETECTED CODE CHANGE]" << std::endl;
             std::cout << "[SYNZ] Reviewing Code..." << std::endl;
             
             // Prompt designed for Code Review
             std::string prompt = "Review this code for bugs. Be concise.\n" + new_code;
             std::string feedback = brain.infer(prompt);
             link.send_reaction(feedback);
        }

        // 3. Logic Bridge (The Face's Backend)
        sockaddr_in sender;
        std::string logic_req = udp_bridge.receive(sender);
        if (!logic_req.empty()) {
             std::cout << "[BRIDGE] Processing: " << logic_req << std::endl;
             std::string ans = brain.infer(logic_req);
             udp_bridge.reply(ans, sender);
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    return 0;
}