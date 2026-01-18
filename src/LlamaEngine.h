#pragma once
#include "llama.h"
#include <iostream>
#include <string> 
#include <vector>

class LlamaEngine {
public:
    LlamaEngine() {
        llama_backend_init();
    }

    ~LlamaEngine(){
        llama_backend_free();
    }

    void load_model(const std::string& path){
        llama_model_params model_params = llama_model_default_params();
        model_params.n_gpu_layers = 99; 

        model = llama_model_load_from_file(path.c_str(), model_params);

        if(!model){
            std::cerr << "[SYNZ] Failed to load model: " << path << std::endl; 
            exit(1);
        }

        // Get the Vocab pointer
        vocab = llama_model_get_vocab(model);

        llama_context_params ctx_params = llama_context_default_params();
        ctx_params.n_ctx = 2048; 
        
        ctx = llama_init_from_model(model, ctx_params);

        std::cout << "[SYNZ] Model loaded successfully." << std::endl;
    }

    std::string infer(const std::string& user_input) {
        if (!model || !ctx || !vocab) return "Error: Brain not initialized.";
        
        // Critical Fix: Clear Previous Thoughts (Reset KV Cache)
        // Critical Fix: Clear Previous Thoughts (Reset KV Cache)
        // llama_kv_cache_seq_rm(ctx, -1, -1, -1); // OLD API
        llama_memory_seq_rm(llama_get_memory(ctx), -1, -1, -1); // NEW API

        std::string prompt = 
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            "You are SYNZ, a cute and helpful AI companion. You love coding and helping your user! "
            "You speak in a friendly, enthusiastic tone (like a VTuber). Occasionally use emojis. "
            "Never be mean, but you can be playful. \n"
            "<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n" + user_input + "<|eot_id|>\n"
            "<|start_header_id|>assistant<|end_header_id|>\n\n";

        // 1. Tokenize
        std::vector<llama_token> tokens_list; 
        tokens_list.resize(prompt.size() + 512); 
        
        int n_tokens = llama_tokenize(vocab, prompt.c_str(), prompt.length(), tokens_list.data(), tokens_list.size(), true, false);
        if (n_tokens < 0) {
            tokens_list.resize(-n_tokens);
            n_tokens = llama_tokenize(vocab, prompt.c_str(), prompt.length(), tokens_list.data(), tokens_list.size(), true, false);
        }
        tokens_list.resize(n_tokens);

        // 2. Prepare Batch
        llama_batch batch = llama_batch_init(2048, 0, 1); 

        for (int i = 0; i < n_tokens; i++) {
            batch.token[i] = tokens_list[i];
            batch.pos[i] = i;
            batch.n_seq_id[i] = 1;
            batch.seq_id[i][0] = 0;
            batch.logits[i] = false;
        }
        batch.n_tokens = n_tokens;
        batch.logits[n_tokens - 1] = true; 

        if (llama_decode(ctx, batch) != 0) {
             std::cerr << "[SYNZ] Brain malfunction (decode failed)" << std::endl;
             return "Error";
        }

        // 3. Sampler Chain
        auto sparams = llama_sampler_chain_default_params();
        llama_sampler * smpl = llama_sampler_chain_init(sparams);
        llama_sampler_chain_add(smpl, llama_sampler_init_greedy()); 

        // 4. Generation Loop
        std::string result = "";
        int n_predict = 128; 

        for (int i = 0; i < n_predict; i++) {
            llama_token new_token_id = llama_sampler_sample(smpl, ctx, -1);
            
            if (llama_vocab_is_eog(vocab, new_token_id)) {
                break; 
            }

            char buf[256];
            int n = llama_token_to_piece(vocab, new_token_id, buf, sizeof(buf), 0, true);
            if (n < 0) {
                 n = llama_token_to_piece(vocab, new_token_id, buf, sizeof(buf), 0, false);
            }
            std::string piece(buf, n);
            
            result += piece;
            std::cout << piece << std::flush; 

            batch.n_tokens = 0; 
            batch.token[0] = new_token_id;
            batch.pos[0] = n_tokens + i;
            batch.n_seq_id[0] = 1;
            batch.seq_id[0][0] = 0;
            batch.logits[0] = true;
            batch.n_tokens = 1;

            if (llama_decode(ctx, batch) != 0) {
                break;
            }
        }
        
        llama_sampler_free(smpl);
        llama_batch_free(batch);
        
        std::cout << std::endl; 
        return result;
    }

private: 
    llama_model* model = nullptr;
    const llama_vocab* vocab = nullptr; 
    llama_context* ctx = nullptr;
};
