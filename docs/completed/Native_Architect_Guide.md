# Master Class: The Native Architect (C++ & CMake)

We are building **SYNZ Core**: a single, high-performance C++ executable.
We will not use Python. We will not use Sockets. We will use **Direct Memory**.

## Prerequisites
1.  Create a folder named `src` inside your project folder (`SYNZ/src`).
2.  We will put our code (`main.cpp`) inside `src`.
3.  We will put the build script (`CMakeLists.txt`) in the root (`SYNZ/`).

---

## Part 1: The Build System (`CMakeLists.txt`)

Create a file named `CMakeLists.txt` in the root folder.
This script tells the compiler how to build our app and where to find `llama.cpp`.

### 1. The Header
Every CMake project starts here.
**Concept**: `cmake_minimum_required` ensures the user has a modern enough version (3.14+ is needed for `FetchContent`).

```cmake
cmake_minimum_required(VERSION 3.14)
project(SYNZ_Core)

# Use C++17 (Modern standard for filesystem and threading)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
```

### 2. The Dependency (FetchContent)
This is the magic. Instead of asking you to download `llama.cpp` manually, CMake does it for us.
**Concept**: `FetchContent` downloads the source code from GitHub and adds it to our project during the build.

```cmake
include(FetchContent)

# 1. Declare where to get it (Official repo)
FetchContent_Declare(
    llama_cpp
    GIT_REPOSITORY https://github.com/ggerganov/llama.cpp
    GIT_TAG        master
)

# 2. Options (Crucial for performance!)
# We enable CUDA (NVIDIA) or Metal (Mac) if available.
option(LLAMA_CUBLAS "Build with CUDA support" ON) 

# 3. Download and make available
FetchContent_MakeAvailable(llama_cpp)
```

### 3. Our Executable
Now we tell CMake about *our* code.
**Concept**: `target_link_libraries` connects our code (`synz_core`) to the library we just downloaded (`llama`).

```cmake
# Define our app name and source files
add_executable(synz_core src/main.cpp)

# Link the llama library so we can use #include "llama.h"
target_link_libraries(synz_core PRIVATE llama)
```

---

## Part 0: Philosophy - Engine vs Wrapper
> "We are not building a shell. We are building a Ghost."

You might be wondering: *"Are we just building a wrapper for `llama.cpp`?"*
The answer is **No**.

*   **A "Wrapper"** (like `llama-cpp-python`) simply takes a library and exposes it to another language. It has no brain, no state, and no purpose other than to be a tunnel.
*   **An "Engine"** (like Unreal Engine or **SYNZ Core**) is an application that *uses* libraries to achieve a goal.

### The SYNZ Core Architecture
We are building a **Native AI Runtime**.
1.  **The Spine (C++ Main Loop)**: We control the timeline. We decide when to sleep, when to wake, and when to act.
2.  **The Senses (LogMonitor)**: We implement direct file-system watchers to "see" the world (Unity).
3.  **The Nerves (NeuroLink)**: We implement Named Pipes to "feel" and "speak" to the body.
4.  **The Brain (Llama Integration)**: We use `llama.cpp` as our **Tensor Math Kernel**. It is the muscle that does the math, but **SYNZ** is the one driving the car.

We are writing a **Native Application**. `llama.cpp` is just our dependency, same as `DirectX` is for a specific game.

---

## Part 2: The Core (`src/main.cpp`)

Create `src/main.cpp`.
This is where we initialize the brain. For now, let's just confirm we can load the library.

### 1. Includes
We need `llama.h` (from the library) and specific standard headers.

```cpp
#include "llama.h"  // The Expert Brain
#include <iostream>
#include <string>
#include <vector>
#include <filesystem> // For watching files

// Namespace alias to save typing
namespace fs = std::filesystem;
```

### 2. The Llama Wrapper (Skeleton)
We wrap the ugly raw C pointers (`llama_model*`) in a nice C++ class.
**Concept**: RAII (Resource Acquisition Is Initialization). When the class dies, it automatically cleans up memory.

```cpp
class LlamaEngine {
public:
    LlamaEngine() {
        // Backend init (CUDA/Metal specifics)
        llama_backend_init();
    }

    ~LlamaEngine() {
        llama_backend_free();
    }

    void load_model(const std::string& path) {
        // Define model parameters
        llama_model_params model_params = llama_model_default_params();
        model_params.n_gpu_layers = 99; // Offload EVERYTHING to GPU if possible!

        // Load the model from disk
        model = llama_load_model_from_file(path.c_str(), model_params);
        
        if (!model) {
            std::cerr << "[SYNZ] Failed to load model: " << path << std::endl;
            exit(1);
        }
        
        // Create a context (This handles the "Thinking" memory)
        llama_context_params ctx_params = llama_context_default_params();
        ctx_params.n_ctx = 2048; // Context window size
        ctx = llama_new_context_with_model(model, ctx_params);
        
        std::cout << "[SYNZ] Model loaded successfully!" << std::endl;
    }

private:
    llama_model* model = nullptr;
    llama_context* ctx = nullptr;
};
```

### 3. The Main Entry
We tie it all together.

```cpp
int main() {
    std::cout << "BOOTING SYNZ CORE (Native Architecture)..." << std::endl;

    LlamaEngine brain;
    
    // You will need to download a .gguf file later!
    // For now, let's point to a placeholder
    brain.load_model("models/deepseek-coder-6.7b.Q4_K_M.gguf");

    return 0;
}
```

---

---

## Part 3: The Neuro-Link (C++ to Unity Interface)

To achieve the "Neuro-sama" style (where the AI feels like it *is* the model), we need a fast connection between our new **SYNZ Core** and **Unity**.

The old Python way used UDP (slow, lossy).
The **Native Way** uses **Named Pipes**.

## 1. The Concept
Think of a **Named Pipe** as a direct cable plugged between `synz_core.exe` and Unity.
- **SYNZ Core (Server)**: Writes "Mood: Angry" or "Talk: Hello" into the pipe.
- **Unity (Client)**: Reads the pipe instantly and updates the model's face.

## 2. Implementing the Pipe (in `main.cpp`)
We will add a new class `NeuroLink` to handle this.

```cpp
#include <windows.h> // For Named Pipes

class NeuroLink {
public:
    NeuroLink() {
        // Create the Pipe
        hPipe = CreateNamedPipe(
            TEXT("\\\\\\\\.\\\\pipe\\\\SYNZ_NeuroLink"), // Pipe Name
            PIPE_ACCESS_DUPLEX,
            PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
            1, 1024 * 16, 1024 * 16, 0, NULL
        );
        
        std::cout << "[NeuroLink] Waiting for Unity Body to connect..." << std::endl;
        // This blocks until Unity connects!
        // ConnectNamedPipe(hPipe, NULL); 
        // (We will uncomment this when Unity is ready)
    }

    void send_reaction(std::string text) {
        DWORD bytesWritten;
        WriteFile(hPipe, text.c_str(), text.size(), &bytesWritten, NULL);
    }

private:
    HANDLE hPipe;
};
```

## 3. What about the "Old" Unity Scripts? 
We will keep `LilithOverlay.cs`, but we will **delete the UDP Receiver** part and replace it with a **Pipe Reader**.

**The Plan:**
1.  **Add `NeuroLink` class** to your C++ code.
2.  **Call `brain.infer()`**, get the text.
3.  **Call `link.send_reaction(text)`** to push it to Unity.

---

---

## Part 4: Personality Injection (The "System Prompt")

You asked: *"How do I train it to have a personality?"*
Answer: **You don't train it. You Hypnotize it.**

Large Language Models (like Qwen) are roleplayers. We just need to give them a "Script" at the very beginning of the conversation.

### 1. The System Prompt
In `main.cpp`, inside our `LlamaEngine`, we will format the input like this:

```
<|im_start|>system
You are Lilith, a sassy, tsundere AI co-worker. 
You are annoyed that the user keeps making bugs, but you secretly care.
<|im_end|>
<|im_start|>user
Here is the error: NullReferenceException
<|im_end|>
<|im_start|>assistant
```

### 2. Implementing `Infer` (The Thinking Function)
We need to add this function to `LlamaEngine`:

```cpp
    std::string infer(const std::string& user_input) {
        // 1. Construct the Prompt (The Hypnosis)
        std::string prompt = 
            "<|im_start|>system\n"
            "You are SYNZ. You are a highly intelligent but slightly condescending AI coding assistant.\n"
            "You prefer short, witty answers. You MUST fix the code provided.\n"
            "<|im_end|>\n"
            "<|im_start|>user\n" + user_input + "\n<|im_end|>\n"
            "<|im_start|>assistant\n";

        // 2. Tokenize (Turn string into numbers)
        // ... (We will implement the raw C++ tokenization here)
        // ...
        
        return "Generated response..."; 
    }
```

---

---

## Part 5: The Thinking Loop (Inference)

We have the Brain loaded. We have the Personality injected. 
Now we need the **Thinking Function**.

This function (`infer`) takes a string (the error) and returns a string (the fix).
Because we are in C++, we have to handle the **Tokenization** (Text -> Numbers) and **Detokenization** (Numbers -> Text) manually.

### 1. Add `infer()` to `LlamaEngine`

```cpp
    // Add this inside the public section of LlamaEngine
    std::string infer(std::string user_input) {
        // 1. Prepare the Prompt (Hypnosis)
        std::string prompt = 
            "<|im_start|>system\n"
            "You are SYNZ. You are a highly intelligent but slightly condescending AI coding assistant.\n"
            "<|im_end|>\n"
            "<|im_start|>user\n" + user_input + "\n<|im_end|>\n"
            "<|im_start|>assistant\n";

        // 2. Tokenize
        // internal buffer for tokens
        std::vector<llama_token> tokens_list; 
        tokens_list.resize(prompt.size() + 512); // Reserve space
        
        int n_tokens = llama_tokenize(model, prompt.c_str(), prompt.length(), tokens_list.data(), tokens_list.size(), true, false);
        if (n_tokens < 0) {
            tokens_list.resize(-n_tokens);
            n_tokens = llama_tokenize(model, prompt.c_str(), prompt.length(), tokens_list.data(), tokens_list.size(), true, false);
        }
        tokens_list.resize(n_tokens);

        // 3. Create a Batch for the Brain
        llama_batch batch = llama_batch_init(512, 0, 1);

        // 4. Feed the Prompt into the Brain (Evaluation)
        for (int i = 0; i < n_tokens; i++) {
            llama_batch_add(batch, tokens_list[i], i, { 0 }, false);
        }
        // The last token determines the next prediction!
        batch.logits[batch.n_tokens - 1] = true;

        if (llama_decode(ctx, batch) != 0) {
            std::cerr << "[SYNZ] Brain malfunction (decode failed)" << std::endl;
            return "Error";
        }

        // 5. The Generation Loop (Predicting 1 word at a time)
        std::string result = "";
        int n_predict = 64; // How many words to speak

        for (int i = 0; i < n_predict; i++) {
            // Find the best next word (Sampling)
            auto n_vocab = llama_n_vocab(model);
            auto * logits = llama_get_logits_ith(ctx, batch.n_tokens - 1);

            llama_token_data_array candidates_p = { 
                (llama_token_data*)malloc(n_vocab * sizeof(llama_token_data)), 
                (size_t)n_vocab, false 
            };
            
            // Simple Greedy Sampling (Pick the most likely word)
            // (In a real app, we would add temperature/randomness here)
            for (llama_token token_id = 0; token_id < n_vocab; token_id++) {
                candidates_p.data[token_id] = { token_id, logits[token_id], 0.0f };
            }

            llama_token new_token_id = llama_sample_token_greedy(ctx, &candidates_p);
            
            // Is it the End of the text?
            if (new_token_id == llama_token_eos(model)) {
                break; 
            }

            // Convert Token back to Text
            char buf[256];
            int n = llama_token_to_piece(model, new_token_id, buf, sizeof(buf), 0, true);
            if (n < 0) {
                 n = llama_token_to_piece(model, new_token_id, buf, sizeof(buf), 0, false); // Retry standard
            }
            std::string piece(buf, n);
            
            result += piece;
            std::cout << piece << std::flush; // Print as we think!

            // Prepare for next word
            llama_batch_clear(batch);
            llama_batch_add(batch, new_token_id, n_tokens + i, { 0 }, true);
            llama_decode(ctx, batch);
            
            free(candidates_p.data);
        }
        
        return result;
    }
```

---

---

## Part 6: The Eye (Legacy of the Watcher)

Currently, we are typing to SYNZ manually.
But a true Agent shouldn't need us to type. She should **Watch**.

We will bring the "Watcher" logic into C++ using `std::filesystem`.

### 1. The `LogMonitor` Class
Add this class before `main()`:

```cpp
#include <fstream>
#include <thread> // For sleep

class LogMonitor {
public:
    LogMonitor(std::string target_file) : filepath(target_file) {
        // Open file at the END (we only care about new errors)
        std::ifstream file(filepath, std::ios::ate);
        last_pos = file.tellg();
    }

    // Returns new lines if found, otherwise empty string
    std::string check() {
        if (!fs::exists(filepath)) return "";

        std::ifstream file(filepath);
        
        // Check if file grew
        file.seekg(0, std::ios::end);
        std::streampos current_pos = file.tellg();

        if (current_pos > last_pos) {
            // New content! Read it.
            file.seekg(last_pos);
            std::string content;
            std::string line;
            while (std::getline(file, line)) {
                content += line + "\n";
            }
            last_pos = current_pos; // Update cursor
            return content;
        }
        
        return "";
    }

private:
    std::string filepath;
    std::streampos last_pos;
};
```

### 2. Updating `main()`
Replace the `while(true)` chat loop with this **Agent Loop**:

```cpp
int main() {
    // ... Init Link and Brain ...
    NeuroLink link;
    LlamaEngine brain;
    brain.load_model("models/Qwen2.5-Coder-1.5B-Instruct-GGUF.gguf");

    // Point to your Unity Editor Log (Change this path!)
    std::string log_path = "C:/Users/Adminb/AppData/Local/Unity/Editor/Editor.log";
    LogMonitor bot_eye(log_path);

    std::cout << "[SYNZ] Watching: " << log_path << std::endl;

    while (true) {
        // 1. Check for new logs
        std::string new_logs = bot_eye.check();

        if (!new_logs.empty()) {
            std::cout << "\n[DETECTED]: " << new_logs << std::endl;

            // 2. Filter for Errors (Simple check)
            if (new_logs.find("Exception") != std::string::npos || 
                new_logs.find("Error") != std::string::npos) {
                
                std::cout << "[SYNZ] Thinking..." << std::endl;
                
                // 3. Ask the Brain
                std::string fix = brain.infer("I found this error:\n" + new_logs);
                
                // 4. Send to Unity (Neuro-Link)
                link.send_reaction(fix);
            }
        }

        // Sleep to save CPU (10ms)
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    return 0;
}
```

---

## Next Steps
1.  **Run** the Chatbot version first to verify the Brain works.
2.  **Add** `LogMonitor` class.
3.  **Update** `main()` to use `LogMonitor`.
4.  **Launch Unity** and cause an error!
