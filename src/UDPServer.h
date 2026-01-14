#pragma once
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>
#include <iostream>

#pragma comment(lib, "ws2_32.lib") // Auto-link for MSVC

class UDPServer {
public:
    UDPServer(int port) : port(port) {
        // Initialize Winsock
        WSAStartup(MAKEWORD(2, 2), &wsaData);

        // Create Socket
        sockfd = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd == INVALID_SOCKET) {
            std::cerr << "[UDP] Failed to create socket." << std::endl;
            return;
        }

        // Set Non-Blocking Mode
        u_long mode = 1;
        ioctlsocket(sockfd, FIONBIO, &mode);

        // Bind
        sockaddr_in serverAddr;
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(port);
        serverAddr.sin_addr.s_addr = INADDR_ANY;

        if (bind(sockfd, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            std::cerr << "[UDP] Bind failed on port " << port << std::endl;
        } else {
            std::cout << "[UDP] Listening on port " << port << std::endl;
        }
    }

    ~UDPServer() {
        closesocket(sockfd);
        WSACleanup();
    }

    // Returns empty string if no data
    std::string receive(sockaddr_in& senderAddr) {
        char buffer[4096];
        int senderLen = sizeof(senderAddr);
        
        int bytesReceived = recvfrom(sockfd, buffer, 4096, 0, (sockaddr*)&senderAddr, &senderLen);
        
        if (bytesReceived > 0) {
            buffer[bytesReceived] = '\0';
            return std::string(buffer);
        }
        return "";
    }

    void reply(const std::string& message, sockaddr_in& targetAddr) {
        sendto(sockfd, message.c_str(), message.size(), 0, (sockaddr*)&targetAddr, sizeof(targetAddr));
    }

private:
    WSADATA wsaData;
    SOCKET sockfd;
    int port;
};
