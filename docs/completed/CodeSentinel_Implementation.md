# 🛡️ Code Sentinel: Implementing "Grammarly for Code"

We are going to give SYNZ the ability to watch your **C# Source Code** while you type, not just your Error Logs.
This allows her to say: *"Hey, you forgot a semicolon on line 42"* **before** you even compile.

## The Plan
1.  Create a new `CodeMonitor` class in `src/main.cpp`.
2.  Use `std::filesystem` to recursively search for `.cs` files.
3.  Track the `last_write_time` of every file to detect changes.
4.  When a file changes, read it and send it to **The Brain**.

---

## Part 1: The `CodeMonitor` Class

Create a new file: `src/CodeMonitor.h`.

```cpp
#pragma once
#include <string>
#include <fstream>
#include <filesystem>
#include <iostream>
#include <map>

namespace fs = std::filesystem;

class CodeMonitor {
public:
    CodeMonitor(std::string target_dir) : project_dir(target_dir) {
        // Initial scan to remember current timestamps
        scan_files(true);
    }


    // Returns formatted code if a file changed, otherwise ""
    std::string check() {
        return scan_files();
    }

private:
    std::string project_dir;
    std::map<std::string, fs::file_time_type> file_stamps;

    std::string scan_files() {
        if (!fs::exists(project_dir)) return "";

        for (const auto& entry : fs::recursive_directory_iterator(project_dir)) {
            if (entry.is_regular_file() && entry.path().extension() == ".cs") {
                
                auto current_time = fs::last_write_time(entry);
                std::string path_str = entry.path().string();

                // If file is new OR modified
                if (file_stamps.find(path_str) == file_stamps.end() || 
                    file_stamps[path_str] != current_time) {
                    
                    file_stamps[path_str] = current_time;
                    
                    // Return the file content for analysis
                    return read_file(path_str);
                }
            }
        }
        return "";
    }

    std::string read_file(const std::string& path) {
        std::ifstream file(path);
        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        return "FILENAME: " + path + "\nCODE:\n" + content;
    }
};
```

---

## Part 2: Connect to the Brain

Inside `src/main.cpp`:

1.  Include the new header: `#include "CodeMonitor.h"`
2.  Add the Sentinel to our loop.

```cpp
    // ... existing includes ...
    #include "CodeMonitor.h"

    int main() {
    // ... existing setup ...
    
    // 1. Point to your Assets folder
    CodeMonitor sentinel("C:/Users/Adminb/OneDrive/Documents/Projects/SYNZ/Assets/Scripts");
    
    std::cout << "Watching Code: " << "C:/Users/Adminb/OneDrive/Documents/Projects/SYNZ/Assets/Scripts" << std::endl;

    while (true) {
        // ... existing log check ...

        // 2. Check for Code Changes
        std::string changed_code = sentinel.check();
        
        if (!changed_code.empty()) {
            std::cout << "[SENTINEL] analyzing change..." << std::endl;
            
            // 3. Ask Brain for Code Review
            std::string prompt = "Review this C# code for errors or improvements:\n" + changed_code;
            std::string feedback = brain.infer(prompt);
            
            // 4. Send to Unity
            link.send_reaction("CODE REVIEW: " + feedback);
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Relax a bit
    }
```

---

## Warning: Token Limits
Reviewing *entire files* eats up the 2048 token limit fast. 
For this prototype, it works for small scripts. For production, we would need to implement **Git Diff** logic to only read the *changed lines*.
