"""Core agent logic - DO NOT CHANGE unless adding NEW capability types"""
import json
import streamlit as st
from tools.text_tools import TEXT_MODELS
from tools.image_tools import IMAGE_MODELS
#from tools.video_tools import VIDEO_MODELS

# Load configuration
with open("config.json", "r") as f:
    config = json.load(f)

def detect_task(user_input):
    """Figure out what the user wants"""
    text = user_input.lower()
    
    # Check for video
    if any(word in text for word in config["video_keywords"]):
        return "video"
    
    # Check for image
    if any(word in text for word in config["image_keywords"]):
        return "image"
    
    # Default to text
    return "text"

def execute_task(task_type, prompt):
    """Run the task using configured models"""
    
    if task_type == "text":
        model_name = config["default_text_model"]
        model_func = TEXT_MODELS.get(model_name)
        if model_func:
            return model_func(prompt)
        else:
            return f"❌ Text model '{model_name}' not found. Available: {list(TEXT_MODELS.keys())}"
    
    elif task_type == "image":
        model_name = config["default_image_model"]
        model_func = IMAGE_MODELS.get(model_name)
        if model_func:
            image_url = model_func(prompt)
            # Return as dict so main.py knows it's an image
            return {"type": "image", "content": image_url}
        else:
            return f"❌ Image model '{model_name}' not found. Available: {list(IMAGE_MODELS.keys())}"
    
    elif task_type == "video":
        model_name = config["default_video_model"]
        model_func = VIDEO_MODELS.get(model_name)
        if model_func:
            video_path = model_func(prompt)
            return f'<video controls src="{video_path}" type="video/mp4" />'
        else:
            return f"❌ Video model '{model_name}' not found. Available: {list(VIDEO_MODELS.keys())}"
    
    else:
        return f"❌ Unknown task type: {task_type}"

def get_available_models():
    """See what models are currently available"""
    return {
        "text": list(TEXT_MODELS.keys()),
        "image": list(IMAGE_MODELS.keys()),
        "video": list(VIDEO_MODELS.keys()),
    }
# ============================================
# CHAT MEMORY SYSTEM
# ============================================

import json
import os
from datetime import datetime

MEMORY_FILE = "chat_memory.json"

def load_memory():
    """Load saved memory from file"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"user_info": {}, "session_id": None}
    return {"user_info": {}, "session_id": None}

def save_memory(memory):
    """Save memory to file"""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def extract_user_info(user_input, response):
    """Extract personal information from conversation"""
    memory = load_memory()
    user_info = memory.get("user_info", {})
    text_lower = user_input.lower()
    
    # Detect name
    if "my name is" in text_lower:
        parts = user_input.split("my name is")
        if len(parts) > 1:
            name = parts[1].strip().split()[0]
            user_info["name"] = name
            memory["user_info"] = user_info
            save_memory(memory)
            return f"Got it, {name}! I'll remember that."
    
    # Detect likes
    if "i like" in text_lower:
        parts = user_input.split("i like")
        if len(parts) > 1:
            like = parts[1].strip().split('.')[0]
            user_info["likes"] = user_info.get("likes", [])
            if like not in user_info["likes"]:
                user_info["likes"].append(like)
            memory["user_info"] = user_info
            save_memory(memory)
            return f"Got it! I'll remember you like {like}."
    
    return None

def get_personalized_context(user_input):
    """Add memory context to the prompt"""
    memory = load_memory()
    user_info = memory.get("user_info", {})
    
    if not user_info:
        return user_input
    
    context = "Previous information you know about the user:\n"
    if "name" in user_info:
        context += f"- User's name is {user_info['name']}\n"
    if "likes" in user_info and user_info["likes"]:
        context += f"- User likes: {', '.join(user_info['likes'])}\n"
    
    # Check if asking about stored info
    text_lower = user_input.lower()
    if "my name" in text_lower and "name" in user_info:
        return f"The user is asking about their name. Their name is {user_info['name']}. Respond naturally."
    if "what do i like" in text_lower or "my likes" in text_lower:
        if "likes" in user_info and user_info["likes"]:
            return f"The user asked what they like. They like: {', '.join(user_info['likes'])}. Respond naturally."
    
    return f"{context}\nCurrent user message: {user_input}"
