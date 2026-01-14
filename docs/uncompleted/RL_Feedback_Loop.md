# 🧬 RL-Lite: Reinforcement Loop Specification

**Goal**: Allow SYNZ to learn from user feedback (Thumbs Up/Down).
**Status**: Planned (Uncompleted).

## 1. The Concept
We don't need PPO (Proximal Policy Optimization) yet. We just need **Dataset Accumulation**.
*   **If User Likes**: Save current context + response to `training_data.txt`.
*   **If User Dislikes**: Do nothing (or remove/penalize).

## 2. The Protocol (`!good` / `!bad`)
Since we don't have buttons yet, we use chat commands.

*   **User**: "Write a function."
*   **SYNZ**: "No. Do it yourself. <TSUN>"
*   **User**: "!good"
*   **SYNZ**: (Internal: *Appends previous interaction to data*) "Noted. I'll stay s-sassy."

## 3. Implementation (`face_server.py`)

```python
history = [] # Stores last few turns

def handle_feedback(user_input):
    if user_input == "!good":
        if len(history) > 0:
            # Append last conversation to training file
            with open("data/training_data.txt", "a") as f:
                f.write(history[-1])
            return "Memory reinforced!"
    return None
```

## 4. The Sleep Cycle
Data on disk doesn't change the brain *immediately*.
The brain only updates when you run `train_scratch.py`.
**Idea**: Create a `reboot_and_train.bat` script that runs the trainer for 100 steps every night.
