#include "Sentinel.h"
#include <iostream>   // For std::cout (printing to console)
#include <fstream>    // For std::ifstream (reading files)
#include <ws2tcpip.h> // For inet_pton (converting IP strings to binary)

// Link the Winsock library. 
// This tells the linker: "Hey, we are using network code, please include ws2_32.lib"
#pragma comment(lib, "ws2_32.lib")

// == CONSTRUCTOR ==
// We use an "Initializer List" (the code after the :) to set variables efficiently.
Sentinel::Sentinel(std::string logDir, std::string targetFile, std::string ip, int port) 
    : log_dir(logDir), target_file(targetFile), server_ip(ip), server_port(port), last_pos(0) 
{
    // Build the full path (e.g., "C:\Logs\Editor.log")
    full_path = log_dir + "\\" + target_file;
    
    // Initialize Windows Sockets (WSA)
    // This is required before doing any networking on Windows.
    WSADATA wsaData;
    // MAKEWORD(2, 2) requests version 2.2 of Winsock.
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "[Fatal] WSAStartup failed" << std::endl;
    }
}

// == DESTRUCTOR ==
Sentinel::~Sentinel() {
    // Clean up the Winsock library usage.
    WSACleanup(); 
}

// == LOGIC: check_log_file ==
// This is the Brain-bridge. It scans the file and extracts meaning.
void Sentinel::check_log_file() {
    // Open the file in "Input" mode (std::ios::in)
    std::ifstream file(full_path, std::ios::in);
    
    // If we can't open it (maybe it's locked?), just abort this check.
    if (!file.is_open()) return;

    // -- Truncation Check --
    // Sometimes Unity restarts and wipes the log. We need to detect this.
    // 1. Jump to the end of the file
    file.seekg(0, std::ios::end);
    // 2. See where we are (file size)
    std::streampos current_size = file.tellg();
    
    // If the file is SMALLER than before, it must have been reset.
    if (current_size < last_pos) last_pos = 0; 

    // If there is NEW data (current size > last position)
    if (current_size > last_pos) {
        // Jump back to where we left off
        file.seekg(last_pos);
        
        std::string line;
        
        // Read line-by-line until the end
        while (std::getline(file, line)) {
            
            // -- CLUE: SLIDING WINDOW LOGIC --
            // 1. Add new line to our memory buffer
            context_buffer.push_back(line);
            
            // 2. If memory is too full ( > 5 lines), forget the oldest line.
            if (context_buffer.size() > MAX_CONTEXT_SIZE) {
                context_buffer.pop_front(); 
            }

            // -- ERROR DETECTION --
            // We check for keywords. This is "Proactive" logic.
            bool isError = false;
            std::string errorType = "";

            // npos means "Not Found". So "!= npos" means "Found it!"
            if (line.find("NullReferenceException") != std::string::npos) {
                isError = true;
                errorType = "NullReference";
            } 
            else if (line.find("error CS") != std::string::npos) { // C# Errors look like "error CS1234"
                isError = true;
                errorType = "CompilationError";
            }

            // -- TRIGGER THE BRAIN --
            if (isError) {
                std::cout << "[Sentinel] !!! Detected " << errorType << " !!!" << std::endl;
                
                // Combine our memory buffer into one big string loop
                std::string contextBlob = "";
                for (const auto& l : context_buffer) {
                    contextBlob += l + "\\n"; // Add a newline character
                }
                
                // Build JSON manually.
                // We send: Type, Error Name, and the FULL CONTEXT (5 lines)
                std::string json = "{\"type\": \"error\", \"error_type\": \"" + errorType + "\", \"content\": \"" + contextBlob + "\"}";
                
                // Send it!
                send_udp(json);
            }
        }
        // Update our bookmark so we don't read these lines again
        last_pos = file.tellg();
    }
}

// == NETWORKING: send_udp ==
void Sentinel::send_udp(const std::string& message) {
    // 1. Create a socket
    // AF_INET = IPv4, SOCK_DGRAM = UDP (Send and forget)
    SOCKET sockfd;
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == INVALID_SOCKET) {
        return; // Failed to create socket
    }

    // 2. Setup destination address
    struct sockaddr_in servaddr;
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(server_port); // htons converts number to network byte order
    
    // Convert string IP ("127.0.0.1") to binary format
    inet_pton(AF_INET, server_ip.c_str(), &servaddr.sin_addr);

    // 3. Send the message
    // sendto() sends the data to the specific address.
    sendto(sockfd, message.c_str(), message.length(), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
    
    // 4. Close the socket (Release resources)
    closesocket(sockfd);
}

// == MAIN LOOP: start ==
void Sentinel::start() {
    std::cout << "[Sentinel] Monitoring: " << full_path << std::endl;
    
    // Do one check immediately, just in case there's already an error waiting.
    check_log_file();

    // -- WINDOWS API MAGIC --
    // We open a monitoring handle to the DIRECTORY itself.
    HANDLE hDir = CreateFile(
        log_dir.c_str(), 
        FILE_LIST_DIRECTORY, // We want to list/watch the dir
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, // Check even if other apps are using it
        NULL, 
        OPEN_EXISTING, 
        FILE_FLAG_BACKUP_SEMANTICS, // Required for opening directories
        NULL
    );

    if (hDir == INVALID_HANDLE_VALUE) return;

    // Buffer for OS notifications
    char buffer[1024];
    DWORD bytesReturned;

    while (true) {
        // ReadDirectoryChangesW blocks (pauses) the program until something happens.
        // This is why it uses 0% CPU! Converting polling to event-driven.
        if (ReadDirectoryChangesW(
            hDir, 
            &buffer, 
            sizeof(buffer), 
            FALSE, // Don't watch subdirectories
            FILE_NOTIFY_CHANGE_LAST_WRITE | FILE_NOTIFY_CHANGE_SIZE, // Wake up on Write or Size change
            &bytesReturned, 
            NULL, 
            NULL
        )) {
            // Something changed! Check our specific file.
            check_log_file();
        }
    }
    CloseHandle(hDir);
}