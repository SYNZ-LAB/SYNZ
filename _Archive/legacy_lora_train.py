import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset
import os

# --- Configuration ---
MODEL_ID = "Qwen/Qwen2.5-Coder-1.5B-Instruct" # Base model (Matches our C++ engine)
OUTPUT_DIR = "synz_face_adapter"
# Resolve path relative to THIS script
script_dir = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(script_dir, "personality_data.json")

def train():
    print(f"[SYNZ] Initializing Training Pipeline for: {MODEL_ID}")
    
    # 1. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token

    # 2. Load Base Model (Quantized for 8GB VRAM)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto"
    )
    
    # 3. Apply LoRA (Low-Rank Adaptation)
    # This freezes the huge model and only trains a tiny adapter (The Personality)
    model = prepare_model_for_kbit_training(model)
    
    peft_config = LoraConfig(
        r=16, 
        lora_alpha=32, 
        lora_dropout=0.05, 
        bias="none", 
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"] # Train Attention layers
    )
    
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 4. Load Dataset
    if not os.path.exists(DATASET_FILE):
        print(f"[ERROR] Missing dataset: {DATASET_FILE}")
        print("Please create a JSON file with your chat logs!")
        return

    dataset = load_dataset("json", data_files=DATASET_FILE, split="train")

    # 5. Training Arguments (Updated for TRL 0.8+)
    from trl import SFTConfig
    
    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        max_steps=200,
        learning_rate=2e-4,
        logging_steps=10,
        optim="paged_adamw_8bit",
        packing=False, # Standard SFT
        dataset_text_field="text" # Now passed to Config!
    )

    # 6. Start Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        tokenizer=tokenizer,
        args=training_args,
    )

    print("[SYNZ] Starting Hypnosis Session (Training)...")
    trainer.train()
    
    print(f"[SYNZ] Training Complete! Adapter saved to: {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)

if __name__ == "__main__":
    train()
