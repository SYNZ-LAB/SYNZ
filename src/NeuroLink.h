#pragma once
#include <windows.h>
#include <string>
#include <iostream>

class NeuroLink {
public:
    NeuroLink() {
        hPipe = CreateNamedPipe(
            TEXT("\\\\.\\pipe\\SYNZ_NeuroLink"),
            PIPE_ACCESS_DUPLEX,
            PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
            1, 1024 * 16, 1024 * 16, 0, NULL
        );
        
        if (hPipe != INVALID_HANDLE_VALUE) {
             std::cout << "[NeuroLink] Pipe created. Waiting for Unity Body..." << std::endl;
             ConnectNamedPipe(hPipe, NULL);
             std::cout << "[NeuroLink] Body Connected!" << std::endl;
        }
    }

    void send_reaction(const std::string& text) {
        if (hPipe == INVALID_HANDLE_VALUE) return;
        DWORD bytesWritten;
        WriteFile(hPipe, text.c_str(), text.size(), &bytesWritten, NULL);
    }

private:
    HANDLE hPipe;
};
