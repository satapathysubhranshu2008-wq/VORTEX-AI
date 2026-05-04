"""Chat Manager - Full conversation management"""

import json
import os
from datetime import datetime

CHATS_FILE = "all_chats.json"

def load_all_chats():
    """Load all saved conversations"""
    if os.path.exists(CHATS_FILE):
        try:
            with open(CHATS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_all_chats(chats):
    """Save all conversations to file"""
    with open(CHATS_FILE, 'w') as f:
        json.dump(chats, f, indent=2)

def create_new_chat():
    """Create a new empty chat"""
    chats = load_all_chats()
    
    chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    chat_name = f"Chat {len(chats) + 1}"
    
    chats[chat_id] = {
        "name": chat_name,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "messages": []
    }
    
    save_all_chats(chats)
    return chat_id

def delete_chat(chat_id):
    """Delete a specific chat"""
    chats = load_all_chats()
    if chat_id in chats:
        del chats[chat_id]
        save_all_chats(chats)
        return True
    return False

def rename_chat(chat_id, new_name):
    """Rename a chat"""
    chats = load_all_chats()
    if chat_id in chats:
        chats[chat_id]["name"] = new_name
        chats[chat_id]["updated"] = datetime.now().isoformat()
        save_all_chats(chats)
        return True
    return False

def add_message_to_chat(chat_id, role, content, image=None):
    """Add a message to a specific chat"""
    chats = load_all_chats()
    
    if chat_id not in chats:
        return False
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    if image:
        message["image"] = image
    
    chats[chat_id]["messages"].append(message)
    chats[chat_id]["updated"] = datetime.now().isoformat()
    
    # Auto-rename first few messages
    if len(chats[chat_id]["messages"]) == 2 and chats[chat_id]["name"].startswith("Chat"):
        first_user_msg = next((m["content"][:30] for m in chats[chat_id]["messages"] if m["role"] == "user"), None)
        if first_user_msg:
            chats[chat_id]["name"] = first_user_msg + "..."
    
    save_all_chats(chats)
    return True

def get_chat_messages(chat_id):
    """Get all messages for a specific chat"""
    chats = load_all_chats()
    if chat_id in chats:
        return chats[chat_id]["messages"]
    return []

def get_all_chat_list():
    """Get list of all chats with metadata"""
    chats = load_all_chats()
    chat_list = []
    for chat_id, chat_data in chats.items():
        chat_list.append({
            "id": chat_id,
            "name": chat_data["name"],
            "created": chat_data["created"],
            "updated": chat_data["updated"],
            "message_count": len(chat_data["messages"])
        })
    # Sort by most recent
    chat_list.sort(key=lambda x: x["updated"], reverse=True)
    return chat_list