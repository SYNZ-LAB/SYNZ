# Tutorial: Building the Sentinel (C++)

This guide teaches you how to architect a high-performance system agent. We aren't just writing scripts; we are building a **stateful service**.

---

## Part 1: The Contract (`Sentinel.h`)

Open `TheWatcher/Sentinel.h`. This file defines the **Interface** (what it does) and **State** (what it knows).

### 1. The Setup (Dependencies)
We need specific libraries to give our Sentinel powers.
*   **Networking**: `winsock2.h` (Must be included *before* `windows.h` to avoid conflicts).
*   **Memory**: `deque` (Double-Ended Queue). We use this for the "Sliding Window" because it's optimized for pushing/popping from ends, unlike `vector` which shifts all elements.

**Type this:**
```cpp
#pragma once // Prevents circular inclusion (standard modern C++)

#include <string>
#include <deque>
#include <vector>
#include <winsock2.h>
#include <windows.h>
```

### 2. The Class Structure
We encapsulate the agent in a class. This allows us to spawn multiple Sentinels later if we want (e.g., one for Unity logs, one for Server logs) as a "Swarm".

**Type this:**
```cpp
class Sentinel {
public:
    // Constructor: Needs to know WHERE to look and WHO to talk to.
    Sentinel(std::string logDir, std::string targetFile, std::string serverIp, int serverPort);
    
    // Destructor: Clean shutdown is crucial for C++ services.
    ~Sentinel();

    // The heartbeat loop.
    void start();

private:
    // == INTERNAL BEHAVIOR ==
    
    // The Core Mechanic: Reads the file and updates memory.
    void check_log_file();
    
    // The Voice: Speak to the Brain via UDP.
    void send_udp(const std::string& message);
    
    // == STATE VARIABLES ==
    
    // Config
    std::string log_dir;
    std::string target_file;
    std::string full_path;
    std::string server_ip;
    int server_port;
    
    // Memory
    std::streampos last_pos; // Cursor position in the file (so we don't re-read old lines)
    std::deque<std::string> context_buffer; // Short-term memory (RAM)
    const int MAX_CONTEXT_SIZE = 5; // How much context to keep
};
```

---

## Part 2: The Logic (`Sentinel.cpp`)

Create `TheWatcher/Sentinel.cpp`. This is the implementation.

### 1. Constructor & Initialization
We use an **Initializer List** (`: variable(value)`) for performance. It constructs the members directly rather than assigning them later.

**Type this:**
```cpp
#include "Sentinel.h"
#include <iostream>
#include <fstream>
#include <ws2tcpip.h> // Modern IP address conversion (inet_pton)

// Link the Winsock library strictly for this file
#pragma comment(lib, "ws2_32.lib")

Sentinel::Sentinel(std::string logDir, std::string targetFile, std::string ip, int port) 
    : log_dir(logDir), target_file(targetFile), server_ip(ip), server_port(port), last_pos(0) 
{
    full_path = log_dir + "\\" + target_file;
    
    // 1. Initialize Windows Sockets (WSA)
    // MAKEWORD(2, 2) requests version 2.2 of Winsock.
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "[Fatal] WSAStartup failed" << std::endl;
    }
}

Sentinel::~Sentinel() {
    WSACleanup(); // Always clean up your toys
}
```

### 2. The "Intelligence" (`check_log_file`)
This is where the **Context Logic** lives.
*   **Concept**: If we just send the error line, the Brain has no clue *why* it happened.
*   **Solution**: We keep a buffer of the last 5 lines. When an error hits, we snapshot that buffer.

**Type this:**
```cpp
void Sentinel::check_log_file() {
    std::ifstream file(full_path, std::ios::in);
    if (!file.is_open()) return;

    // Handle File Truncation (Unity restarts -> log clears)
    file.seekg(0, std::ios::end);
    std::streampos current_size = file.tellg();
    if (current_size < last_pos) last_pos = 0; // Reset cursor

    if (current_size > last_pos) {
        file.seekg(last_pos);
        std::string line;
        
        while (std::getline(file, line)) {
            // [TEACHING MOMENT] Sliding Window Logic
            context_buffer.push_back(line);
            if (context_buffer.size() > MAX_CONTEXT_SIZE) {
                context_buffer.pop_front(); // Remove oldest line
            }

            // Proactive Detection
            if (line.find("NullReferenceException") != std::string::npos) {
                std::cout << "[Sentinel] !!! NullReferenceException Detected !!!" << std::endl;
                
                // Pack the Context
                std::string contextBlob = "";
                for (const auto& l : context_buffer) contextBlob += l + "\\n";
                
                // Manual JSON construction (fast & dependency-free)
                std::string json = "{\"type\": \"error\", \"content\": \"" + contextBlob + "\"}";
                send_udp(json);
            }
        }
        last_pos = file.tellg();
    }
}
```

### 3. networking (`send_udp`)
This is standard boilerplate, but crucial. `sockaddr_in` struct defines the destination.

**Type this:**
```cpp
void Sentinel::send_udp(const std::string& message) {
    SOCKET sockfd;
    struct sockaddr_in servaddr;

    // Create a UDP socket (SOCK_DGRAM)
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == INVALID_SOCKET) return;

    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(server_port); // Host TO Network Short (endianness flip)
    inet_pton(AF_INET, server_ip.c_str(), &servaddr.sin_addr);

    sendto(sockfd, message.c_str(), message.length(), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
    closesocket(sockfd);
}
```

### 4. The Loop (`start`)
We use `ReadDirectoryChangesW` to ask the OS kernel to wake us up only when the file changes. This keeps CPU usage near 0%.

**Type this:**
```cpp
void Sentinel::start() {
    std::cout << "[Sentinel] Monitoring: " << full_path << std::endl;
    check_log_file(); // Initial scan

    // Get a handle to the DIRECTORY, not the file
    HANDLE hDir = CreateFile(
        log_dir.c_str(), FILE_LIST_DIRECTORY, 
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL
    );

    if (hDir == INVALID_HANDLE_VALUE) return;

    char buffer[1024];
    DWORD bytesReturned;

    while (true) {
        // This function BLOCKS until an event occurs (Zero CPU usage waiting)
        if (ReadDirectoryChangesW(
            hDir, &buffer, sizeof(buffer), FALSE,
            FILE_NOTIFY_CHANGE_LAST_WRITE | FILE_NOTIFY_CHANGE_SIZE,
            &bytesReturned, NULL, NULL
        )) {
            check_log_file();
        }
    }
    CloseHandle(hDir);
}
```

---

## Part 3: The Entry (`main.cpp`)

Finally, replace the chaos in `main.cpp` with a clean instantiation of your agent.

**Type this:**
```cpp
#include "Sentinel.h"
#include <iostream>

int main() {
    // Config: Adjust these if your paths are different!
    std::string logDir = "C:\\Users\\Adminb\\AppData\\Local\\Unity\\Editor";
    std::string targetFile = "Editor.log";
    
    Sentinel sentinel(logDir, targetFile, "127.0.0.1", 5005);
    sentinel.start();
    
    return 0;
}
```
