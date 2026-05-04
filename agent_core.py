"""Core agent logic - Video removed for deployment"""

import json
import streamlit as st
from tools.text_tools import TEXT_MODELS
from tools.image_tools import IMAGE_MODELS

# Empty video models (not used)
VIDEO_MODELS = {}

# Load configuration
with open("config.json", "r") as f:
    config = json.load(f)

def detect_task(user_input):
    """Figure out what the user wants"""
    text = user_input.lower()
    
    # Check for image
    if any(word in text for word in config["image_keywords"]):
        return "image"
    
    # Default to text
    return "text"

def execute_task(task_type, prompt):
    """Run the task using configured models"""
    
    if task_type == "image":
        model_name = config["default_image_model"]
        model_func = IMAGE_MODELS.get(model_name)
        if model_func:
            image_url = model_func(prompt)
            return {"type": "image", "content": image_url}
        else:
            return f"❌ Image model '{model_name}' not found"
    
    else:  # text
        model_name = config["default_text_model"]
        model_func = TEXT_MODELS.get(model_name)
        if model_func:
            return model_func(prompt)
        else:
            return f"❌ Text model '{model_name}' not found"

def get_available_models():
    """See what models are currently available"""
    return {
        "text": list(TEXT_MODELS.keys()),
        "image": list(IMAGE_MODELS.keys()),
        "video": []
    }

def load_memory():
    """Load memory from file"""
    import os
    MEMORY_FILE = "chat_memory.json"
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"user_info": {}}
    return {"user_info": {}}

def get_personalized_context(user_input):
    """Add memory context to prompt"""
    memory = load_memory()
    user_info = memory.get("user_info", {})
    
    if not user_info:
        return user_input
    
    context = "Previous information you know about the user:\n"
    if "name" in user_info:
        context += f"- User's name is {user_info['name']}\n"
    if "likes" in user_info and user_info["likes"]:
        context += f"- User likes: {', '.join(user_info['likes'])}\n"
    
    return f"{context}\nCurrent user message: {user_input}"

def extract_user_info(user_input, response):
    """Extract personal information from conversation"""
    import os
    import json
    MEMORY_FILE = "chat_memory.json"
    
    memory = load_memory()
    user_info = memory.get("user_info", {})
    text_lower = user_input.lower()
    
    if "my name is" in text_lower:
        parts = user_input.split("my name is")
        if len(parts) > 1:
            name = parts[1].strip().split()[0]
            user_info["name"] = name
            memory["user_info"] = user_info
            with open(MEMORY_FILE, 'w') as f:
                json.dump(memory, f)
            return f"Got it, {name}! I'll remember that."
    
    if "i like" in text_lower:
        parts = user_input.split("i like")
        if len(parts) > 1:
            like = parts[1].strip().split('.')[0]
            user_info["likes"] = user_info.get("likes", [])
            if like not in user_info["likes"]:
                user_info["likes"].append(like)
            memory["user_info"] = user_info
            with open(MEMORY_FILE, 'w') as f:
                json.dump(memory, f)
            return f"Got it! I'll remember you like {like}."
    
    return None
