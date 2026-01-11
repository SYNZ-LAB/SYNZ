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
        // Initial scan to remember current timestamps so we don't spam on startup
        scan_files(true);
    }

    // Returns formatted code if a file changed, otherwise ""
    std::string check() {
        return scan_files(false);
    }

private:
    std::string project_dir;
    std::map<std::string, fs::file_time_type> file_stamps;

    std::string scan_files(bool initial_run) {
        if (!fs::exists(project_dir)) return "";

        for (const auto& entry : fs::recursive_directory_iterator(project_dir)) {
            if (entry.is_regular_file() && entry.path().extension() == ".cs") {
                
                auto current_time = fs::last_write_time(entry);
                std::string path_str = entry.path().string();

                // If file is new OR modified
                if (file_stamps.find(path_str) == file_stamps.end() || 
                    file_stamps[path_str] != current_time) {
                    
                    file_stamps[path_str] = current_time;
                    
                    if (!initial_run) {
                        return read_file(path_str);
                    }
                }
            }
        }
        return "";
    }

    std::string read_file(const std::string& path) {
        std::ifstream file(path);
        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        return "[CODE_CHANGE] FILE: " + path + "\nSOURCE:\n" + content;
    }
};
