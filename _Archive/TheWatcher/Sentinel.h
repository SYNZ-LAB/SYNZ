#pragma once // "Pragma Once" tells the compiler: "Only parse this file once, even if included multiple times!"

#include <string>     // For std::string
#include <deque>      // For std::deque (Double Ended Queue) - our Sliding Window buffer
#include <vector>     // For std::vector
#include <winsock2.h> // For Windows Sockets (Networking) - MUST be included before windows.h!
#include <windows.h>  // For Windows API (File Monitoring)

// The Sentinel Class
// This defines the "Blueprint" for our agent.
class Sentinel {
public:
    // Constructor: When we create a Sentinel, we need to give it settings.
    // logDir: Where are the logs?
    // targetFile: Which specific file to watch?
    // serverIp: Where is The Brain?
    // serverPort: Which port is The Brain listening on?
    Sentinel(std::string logDir, std::string targetFile, std::string serverIp, int serverPort);
    
    // Destructor: This runs when the Sentinel is destroyed/deleted. 
    // We use it to clean up the network sockets.
    ~Sentinel();

    // The "Main Loop" of this agent.
    // calls start() to begin watching the directory.
    void start();

private:
    // == INTERNAL BEHAVIOR ==
    
    // check_log_file: The core intelligence. 
    // Reads new lines, maintains context buffer, and detects errors.
    void check_log_file();
    
    // send_udp: The voice.
    // Takes a string message and blasts it over the network to The Brain.
    void send_udp(const std::string& message);
    
    // == STATE VARIABLES (Data we remember) ==
    
    // Configuration storage
    std::string log_dir;
    std::string target_file;
    std::string full_path; // Combined log_dir + target_file
    std::string server_ip;
    int server_port;
    
    // Memory
    std::streampos last_pos; // The cursor position in the file. We save this so we don't re-read old lines.
    
    // The "Context Buffer" (Sliding Window)
    // We use a deque because we need to add to the back and remove from the front efficiently.
    std::deque<std::string> context_buffer; 
    
    // Constant: How many lines of history to keep?
    const int MAX_CONTEXT_SIZE = 5; 
};