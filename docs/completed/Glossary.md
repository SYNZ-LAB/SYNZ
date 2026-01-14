# 📖 SYNZ Core: The Technical Glossary

Definitions of the concepts, libraries, and functions used in our Native C++ Architecture.

## 🛠️ Libraries & Headers

### `llama.h`
*   **Definition**: The header file for **llama.cpp**, the library that runs the AI model.
*   **What it does**: Gives us access to the "Brain" functions like `llama_decode` (think) and `llama_tokenize` (read).
*   **Why we use it**: It is the fastest way to run LLMs locally on CPU/GPU without Python.

### `<windows.h>`
*   **Definition**: The massive standard library for Windows OS functions.
*   **What it does**: Gives us access to "Named Pipes" (`CreateNamedPipe`).
*   **Why we use it**: To create the high-speed "Neuro-Link" cable between C++ and Unity.

### `<filesystem>` (`std::filesystem`)
*   **Definition**: A modern C++ library for managing files.
*   **What it does**: Allows us to check file sizes, last modified times, and existence.
*   **Why we use it**: To make the "Watcher" (`LogMonitor`) that detects when Unity writes a new error log.

### `<vector>` (`std::vector`)
*   **Definition**: A dynamic array (list) that can grow or shrink.
*   **What it does**: Stores lists of things.
*   **Why we use it**: To store the list of **Tokens** (numbers) that make up the prompt.

---

## 🧠 AI Concepts

### Tokenization (`llama_tokenize`)
*   **Definition**: Converting Text ("Hello") into Numbers (`[101, 888]`).
*   **Why**: Computers don't understand words, only math. The model processes these numbers.

### Logits
*   **Definition**: A raw score for every word in the dictionary, representing how likely it is to be the next word.
*   **Example**: "The cat sat on the..." -> Logits might say "mat" (99%), "hat" (0.5%), "dog" (0.5%).

### Sampling (`llama_sampler_sample`)
*   **Definition**: The process of picking *one* word from the list of Logits.
*   **Greedy Sampling**: Always picking the highest score (Best for coding).
*   **Random Sampling**: Picking lower scores occasionally (Best for creative writing).

### Context Window (`ctx`)
*   **Definition**: The "Short Term Memory" of the AI.
*   **Limit**: 2048 tokens (in our code). If conversation goes longer, it forgets the beginning.

### Batch (`llama_batch`)
*   **Definition**: A container for sending multiple tokens to the GPU at once.
*   **Why**: Sending 100 tokens in one "Batch" is much faster than sending 1 token 100 times.

---

## 🔌 Systems Engineering

### Named Pipe (`CreateNamedPipe`)
*   **Definition**: A section of shared memory that looks like a file.
*   **Analogy**: A physical tube connecting two programs.
*   **Why**: It is 1000x faster than internet sockets (UDP/TCP) because the data never leaves the RAM.

### Monolith
*   **Definition**: A single executable file (`synz_core.exe`) that does *everything* (Watching + Thinking + Talking).
*   **Opposite**: Microservices (Lots of tiny scripts talking to each other).
*   **Why**: Zero Latency. Immediate reaction.

### IPC (Inter-Process Communication)
*   **Definition**: How two separate programs (C++ Core and Unity Game) talk to each other.
*   **Our Method**: Named Pipes.

---

## 💻 Key Functions in `main.cpp`

*   `llama_backend_init()`: Wakes up the GPU/CPU drivers.
*   `llama_model_load_from_file()`: Reads the `.gguf` file (the brain weights) into RAM.
*   `llama_decode()`: The "Think" button. It processes the batch of numbers.
*   `llama_token_to_piece()`: Detokenization. Turns the predicted number back into a text character.
*   `std::this_thread::sleep_for()`: Pauses the loop for 10ms so we don't melt your CPU checking generic logs too fast.
