import os
from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers, processors

def train_tokenizer(source_paths, vocab_size=50304, save_path="lilith_tokenizer.json"):
    """
    Trains a BPE tokenizer on C#/C++ files found in source_paths.
    """
    # Initialize a tokenizer
    tokenizer = Tokenizer(models.BPE())
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    
    # Special tokens for Lilith's actions and standard special tokens
    special_tokens = [
        "<|endoftext|>",
        "<|padding|>",
        "<ACTION_SMILE>",
        "<ACTION_FROWN>",
        "<ACTION_THINK>",
        "<ACTION_SURPRISE>",
        "<ACTION_LAUGH>",
        "<ACTION_ANGRY>",
        "<ACTION_NEUTRAL>"
    ]

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size, 
        special_tokens=special_tokens,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet()
    )

    # Collect files
    files = []
    for path in source_paths:
        if os.path.isfile(path):
            files.append(path)
        elif os.path.isdir(path):
            for root, dirs, filenames in os.walk(path):
                for f in filenames:
                    if f.endswith(('.cs', '.cpp', '.h', '.hpp', '.c', '.cc')):
                        files.append(os.path.join(root, f))
    
    if not files:
        print("No source files found to train on.")
        return None

    print(f"Training tokenizer on {len(files)} files...")
    tokenizer.train(files, trainer)

    # Post-processing
    tokenizer.post_processor = processors.ByteLevel(trim_offsets=False)
    
    # Save
    tokenizer.save(save_path)
    print(f"Tokenizer saved to {save_path}")
    return tokenizer

def get_tokenizer(path="lilith_tokenizer.json"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Tokenizer file not found at {path}. Please train it first.")
    return Tokenizer.from_file(path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, help="Directory containing C#/C++ code", required=True)
    parser.add_argument("--vocab_size", type=int, default=50304)
    args = parser.parse_args()
    
    train_tokenizer([args.data_dir], vocab_size=args.vocab_size)
