#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <thread>
#include <chrono>
#include <winsock2.h>
#include <windows.h>
#include <ws2tcpip.h>
#include <deque>

#pragma comment(lib, "ws2_32.lib")

// Configuration
const std::string TARGET_LOG_FILENAME = "Editor.log";
// Adjust this path to the actual Unity Editor log path
const std::string LOG_DIR = "C:\\Users\\Adminb\\AppData\\Local\\Unity\\Editor"; 
const std::string SERVER_IP = "127.0.0.1";
const int SERVER_PORT = 5005; // The Brain listens here

void send_udp(const std::string& message) {
    WSADATA wsaData;
    SOCKET sockfd;
    struct sockaddr_in servaddr;

    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed" << std::endl;
        return;
    }

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == INVALID_SOCKET) {
        std::cerr << "Socket creation failed" << std::endl;
        WSACleanup();
        return;
    }

    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP.c_str(), &servaddr.sin_addr);

    sendto(sockfd, message.c_str(), message.length(), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
    
    closesocket(sockfd);
    WSACleanup();
}

// Define a global or static storage for the last 5 lines.
// Hint: std::vector<std::string> or std::deque<std::string> works well.

std::deque<std::string> log_buffer; // Buffer to store the last 5 lines . double ended queu containter that is very fast at adding item to the end and removing them from the front 

std::streampos last_pos = 0;

void check_log_file(const std::string& full_path) {
    std::ifstream file(full_path, std::ios::in);
    if (!file.is_open()) return;

    // If file was truncated (restarted), reset pos
    file.seekg(0, std::ios::end);
    std::streampos current_size = file.tellg();
    
    if (current_size < last_pos) {
        last_pos = 0;
    }

    if (current_size > last_pos) {
        file.seekg(last_pos);
        std::string line;
        while (std::getline(file, line)) {
            // TODO: PHASE 2 - IMPLEMENTATION CLUE #2
            // Add the current 'line' to your storage buffer.
            // If the buffer size > 5, remove the oldest line.

            // Simple keyword matching
            if (line.find("NullReferenceException") != std::string::npos) {
                std::cout << "Detected: NullReferenceException" << std::endl;
                send_udp("{\"type\": \"error\", \"content\": \"NullReferenceException detected\"}");
            }
            else if (line.find("Segmentation fault") != std::string::npos) {
                std::cout << "Detected: Segmentation fault" << std::endl;
                send_udp("{\"type\": \"error\", \"content\": \"Segmentation fault detected\"}");
            }
             else if (line.find("Error") != std::string::npos) {
                // Generic error
                 std::cout << "Detected: Generic Error" << std::endl;
                 
                 // TODO: PHASE 2 - IMPLEMENTATION CLUE #3
                 // Instead of just sending the 'line', loop through your 
                 // buffer and combine all 5 lines into a single string.
                 // Then send that 'context' string in the JSON payload.
                 
                 send_udp("{\"type\": \"error\", \"content\": \"Generic Error detected: " + line + "\"}");
            }
        }
        last_pos = file.tellg();
    }
}

int main() {
    std::cout << "Lilith Watcher Started..." << std::endl;
    std::cout << "Watching: " << LOG_DIR << "\\" << TARGET_LOG_FILENAME << std::endl;

    HANDLE hDir = CreateFile(
        LOG_DIR.c_str(),
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        NULL
    );

    if (hDir == INVALID_HANDLE_VALUE) {
        std::cerr << "Error opening directory handle. Error: " << GetLastError() << std::endl;
        return 1;
    }

    char buffer[1024];
    DWORD bytesReturned;
    
    // Initial check
    check_log_file(LOG_DIR + "\\" + TARGET_LOG_FILENAME);

    while (true) {
        if (ReadDirectoryChangesW(
            hDir,
            &buffer,
            sizeof(buffer),
            FALSE, // Watch subtree? No
            FILE_NOTIFY_CHANGE_LAST_WRITE | FILE_NOTIFY_CHANGE_SIZE,
            &bytesReturned,
            NULL,
            NULL
        )) {
            // Something changed, check the file
            // We could parse the buffer to see WHICH file changed, but for now just checking the target is cheap enough
            // optimization: verify if TARGET_LOG_FILENAME is in the buffer
            
            FILE_NOTIFY_INFORMATION* pNotify = (FILE_NOTIFY_INFORMATION*)buffer;
            std::wstring changedFile(pNotify->FileName, pNotify->FileNameLength / sizeof(WCHAR));
            
            // Convert to string for comparison (simple hack)
            std::string changedFileStr(changedFile.begin(), changedFile.end());
            
            if (changedFileStr == TARGET_LOG_FILENAME) {
                 check_log_file(LOG_DIR + "\\" + TARGET_LOG_FILENAME);
            }
            
            // Handle next entry if multiple
            while (pNotify->NextEntryOffset != 0) {
                pNotify = (FILE_NOTIFY_INFORMATION*)((char*)pNotify + pNotify->NextEntryOffset);
                std::wstring nextFile(pNotify->FileName, pNotify->FileNameLength / sizeof(WCHAR));
                std::string nextFileStr(nextFile.begin(), nextFile.end());
                 if (nextFileStr == TARGET_LOG_FILENAME) {
                     check_log_file(LOG_DIR + "\\" + TARGET_LOG_FILENAME);
                }
            }
        }
        // Small sleep to prevent tight loop if something goes wrong with ReadDirectoryChangesW
        // But ReadDirectoryChangesW is blocking, so this is fine.
    }

    CloseHandle(hDir);
    return 0;
}
