#pragma once
#include <string>
#include <fstream>
#include <filesystem>
#include <iostream>

namespace fs = std::filesystem;

class LogMonitor {
public: 
    LogMonitor(std::string target_file) : filepath(target_file){
        std::ifstream file(filepath, std::ios::ate);
        last_pos = file.tellg();
    }

    std::string check(){
        if(!fs::exists(filepath)) return "";

        std::ifstream file(filepath);
        file.seekg(0, std::ios::end);
        std::streampos current_pos = file.tellg();

        if (current_pos > last_pos){
            file.seekg(last_pos);
            std::string content; 
            std::string line;
            while (std::getline(file, line)){
                content += line + "\n";
            }
            last_pos = current_pos; 
            return content; 
        }
        return "";
    }
private: 
    std::string filepath; 
    std::streampos last_pos;
};
