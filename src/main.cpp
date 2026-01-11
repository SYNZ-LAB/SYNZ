#include "LlamaEngine.h"
#include "NeuroLink.h"
#include "LogMonitor.h"
#include "CodeMonitor.h"
#include <thread>

int main(){
    std::cout << "BOOTING SYNZ CORE (Native Architecture)..." << std::endl;
    
    NeuroLink link;
    LlamaEngine brain; 

    // Initialize Brain
    std::string model_path = "models/Qwen2.5-Coder-1.5B-Instruct-GGUF.gguf";
    brain.load_model(model_path); 

    // Initialize Eyes (Log Watcher)
    std::string log_path = "C:/Users/Adminb/AppData/Local/Unity/Editor/Editor.log";
    LogMonitor bot_eye(log_path);
    
    // Initialize Sentinel (Code Watcher) - Pointing to unity_scripts for now
    std::string code_path = "c:/Users/Adminb/OneDrive/Documents/Projects/SYNZ/unity_scripts";
    CodeMonitor sentinel(code_path);

    std::cout << "[SYNZ] Watching Logs: " << log_path << std::endl;
    std::cout << "[SYNZ] Watching Code: " << code_path << std::endl;

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

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    return 0;
}