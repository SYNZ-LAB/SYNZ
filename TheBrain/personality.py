import json
import os
import time

class PersonalityManager:
    def __init__(self, config_path="TheBrain/personality_config.json"):
        self.config_path = config_path
        self.load_config()
        self.last_error_time = time.time()
        self.frustration_level = 0.0

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"current_personality": "default", "personalities": {}}

    def get_current_profile(self):
        p_name = self.data.get("current_personality", "default")
        return self.data.get("personalities", {}).get(p_name, {})

    def process_input(self, input_text):
        current_time = time.time()
        time_diff = current_time - self.last_error_time
        
        if time_diff < 10:
            self.frustration_level = min(self.frustration_level + 0.2, 1.0)
        else: 
            self.frustration_level = max(self.frustration_level - 0.1, 0.0)
            
        self.last_error_time = current_time
        
        profile = self.get_current_profile()
        prefix = profile.get("prefix_tag", "")
        return f"{prefix} {input_text}"

    def process_output(self, raw_action):
        if self.frustration_level > 0.8: 
            return "ANGRY" 
        elif self.frustration_level > 0.5: 
            return "FROWN" 
        elif self.frustration_level > 0.2: 
            return "SMILE" 
        
        return raw_action
