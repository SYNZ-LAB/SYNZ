#include "llama.h"
#include <iostream>
#include <string> 
#include <vector>
#include <filesystem>
#include <windows.h> // Correct header for Named Pipes

namespace fs = std::filesystem;

// --- Part 3: The Neuro-Link (Unity Communication) ---
class NeuroLink {
public:
    NeuroLink() {
        // Create the Pipe
        hPipe = CreateNamedPipe(
            TEXT("\\\\.\\pipe\\SYNZ_NeuroLink"), // Pipe Name (Corrected slashed)
            PIPE_ACCESS_DUPLEX,
            PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
            1, 1024 * 16, 1024 * 16, 0, NULL
        );
        
        // In a real app, we might want to wait for connection in a separate thread
        // or just proceed if not found. For now, we'll confirm it's created.
        if (hPipe != INVALID_HANDLE_VALUE) {
             std::cout << "[NeuroLink] Pipe created. Waiting for Unity Body..." << std::endl;
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

// --- Part 2 & 4 & 5: The Brain ---
class LlamaEngine {
public:
    LlamaEngine() {
        // Initialize the backend (CUDA/Metal detection)
        llama_backend_init();
    }

    ~LlamaEngine(){
        llama_backend_free();
    }

    void load_model(const std::string& path){
        // Config for the model
        llama_model_params model_params = llama_model_default_params();
        model_params.n_gpu_layers = 99;  // Offload everything to GPU if possible 

        // Load model from file
        model = llama_load_model_from_file(path.c_str(), model_params);

        if(!model){
            std::cerr << "[SYNZ] Failed to load model: " << path << std::endl; 
            exit(1);
        }

        // Config for the context (working memory)
        llama_context_params ctx_params = llama_context_default_params();
        ctx_params.n_ctx = 2048; // context window size

        ctx = llama_new_context_with_model(model, ctx_params);

        std::cout << "[SYNZ] Model loaded successfully." << std::endl;
    }

    // The Thinking Loop
    std::string infer(const std::string& user_input) {
        if (!model || !ctx) return "Error: Brain not initialization.";

        // 1. Prepare the Prompt (Hypnosis)
        std::string prompt = 
            "<|im_start|>system\n"
            "You are SYNZ. You are a highly intelligent but slightly condescending AI coding assistant.\n"
            "<|im_end|>\n"
            "<|im_start|>user\n" + user_input + "\n<|im_end|>\n"
            "<|im_start|>assistant\n";

        // 2. Tokenize
        std::vector<llama_token> tokens_list; 
        tokens_list.resize(prompt.size() + 512); 
        
        int n_tokens = llama_tokenize(model, prompt.c_str(), prompt.length(), tokens_list.data(), tokens_list.size(), true, false);
        if (n_tokens < 0) {
            tokens_list.resize(-n_tokens);
            n_tokens = llama_tokenize(model, prompt.c_str(), prompt.length(), tokens_list.data(), tokens_list.size(), true, false);
        }
        tokens_list.resize(n_tokens);

        // 3. Create a Batch
        llama_batch batch = llama_batch_init(512, 0, 1);

        // 4. Feed Prompt
        for (int i = 0; i < n_tokens; i++) {
            llama_batch_add(batch, tokens_list[i], i, { 0 }, false);
        }
        batch.logits[batch.n_tokens - 1] = true;

        if (llama_decode(ctx, batch) != 0) {
             std::cerr << "[SYNZ] Brain malfunction (decode failed)" << std::endl;
             return "Error";
        }

        // 5. Generation Loop
        std::string result = "";
        int n_predict = 128; // Length of response

        for (int i = 0; i < n_predict; i++) {
            auto n_vocab = llama_n_vocab(model);
            auto * logits = llama_get_logits_ith(ctx, batch.n_tokens - 1);

            llama_token_data_array candidates_p = { 
                (llama_token_data*)malloc(n_vocab * sizeof(llama_token_data)), 
                (size_t)n_vocab, false 
            };
            
            for (llama_token token_id = 0; token_id < n_vocab; token_id++) {
                candidates_p.data[token_id] = { token_id, logits[token_id], 0.0f };
            }

            llama_token new_token_id = llama_sample_token_greedy(ctx, &candidates_p);
            
            if (new_token_id == llama_token_eos(model)) {
                free(candidates_p.data);
                break; 
            }

            char buf[256];
            int n = llama_token_to_piece(model, new_token_id, buf, sizeof(buf), 0, true);
            if (n < 0) {
                 n = llama_token_to_piece(model, new_token_id, buf, sizeof(buf), 0, false);
            }
            std::string piece(buf, n);
            
            result += piece;
            std::cout << piece << std::flush; // Print as we think

            llama_batch_clear(batch);
            llama_batch_add(batch, new_token_id, n_tokens + i, { 0 }, true);
            llama_decode(ctx, batch);
            
            free(candidates_p.data);
        }
        std::cout << std::endl; // Newline at end
        return result;
    }

private: 
    llama_model* model = nullptr;
    llama_context* ctx = nullptr;
};

// --- Main Entry ---
int main(){
    std::cout << "BOOTING SYNZ CORE (Native Architecture)..." << std::endl;
    
    // 1. Initialize NeuroLink (The Body)
    NeuroLink link;

    // 2. Initialize Brain
    LlamaEngine brain; 

    // We use Qwen2.5-Coder as our default Expert Model
    std::string model_path = "models/Qwen2.5-Coder-1.5B-Instruct-GGUF.gguf";
    brain.load_model(model_path); 
    
    // 3. Interactive Test Loop (Temporary)
    // In the future, this will be replaced by the File Watcher
    std::string user_input;
    while(true) {
        std::cout << "\n[User]: ";
        std::getline(std::cin, user_input);
        
        if (user_input == "exit") break;
        
        std::cout << "[SYNZ]: ";
        std::string response = brain.infer(user_input);
        
        // Send to Unity!
        link.send_reaction(response);
    }

    return 0;
}