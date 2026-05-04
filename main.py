"""Main Streamlit App - Complete Working Version"""

import streamlit as st
import json
import os
from datetime import datetime
from agent_core import detect_task, execute_task, get_available_models, get_personalized_context, extract_user_info
from chat_manager import (
    load_all_chats, save_all_chats, create_new_chat, delete_chat, 
    rename_chat, add_message_to_chat, get_chat_messages, get_all_chat_list
)

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Voice output
try:
    from tools.voice_tools import speak_text
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False
    def speak_text(text):
        pass

# ============================================
# PAGE SETUP
# ============================================

st.set_page_config(page_title="AI Agent", page_icon="🤖", layout="wide")

# Simple safe CSS


st.title("🤖 AI Agent")
st.caption(f"🧠 Text: {config['default_text_model']} | 🎨 Image: {config['default_image_model']}")

# ============================================
# INITIALIZE SESSION STATE
# ============================================

if "current_chat_id" not in st.session_state:
    chats = load_all_chats()
    if chats:
        st.session_state.current_chat_id = list(chats.keys())[0]
    else:
        st.session_state.current_chat_id = create_new_chat()

if "messages" not in st.session_state:
    st.session_state.messages = get_chat_messages(st.session_state.current_chat_id)

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 💬 Conversations")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_id = create_new_chat()
        st.session_state.current_chat_id = new_id
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    chats = get_all_chat_list()
    
    for chat in chats:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"💬 {chat['name'][:30]}", key=f"chat_{chat['id']}", use_container_width=True):
                st.session_state.current_chat_id = chat['id']
                st.session_state.messages = get_chat_messages(chat['id'])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{chat['id']}"):
                delete_chat(chat['id'])
                if st.session_state.current_chat_id == chat['id']:
                    remaining = get_all_chat_list()
                    if remaining:
                        st.session_state.current_chat_id = remaining[0]['id']
                        st.session_state.messages = get_chat_messages(remaining[0]['id'])
                    else:
                        new_id = create_new_chat()
                        st.session_state.current_chat_id = new_id
                        st.session_state.messages = []
                st.rerun()
    
    st.markdown("---")
    
    current_chats = load_all_chats()
    if st.session_state.current_chat_id in current_chats:
        current_name = current_chats[st.session_state.current_chat_id]["name"]
        new_name = st.text_input("✏️ Rename chat", value=current_name)
        if new_name != current_name:
            rename_chat(st.session_state.current_chat_id, new_name)
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 🧠 Memory")
    from agent_core import load_memory
    memory = load_memory()
    user_info = memory.get("user_info", {})
    
    if user_info:
        st.success(f"👤 {user_info.get('name', 'User')} remembered!")
        if "likes" in user_info and user_info["likes"]:
            st.caption(f"❤️ Likes: {', '.join(user_info['likes'][:2])}")
    
    st.markdown("---")
    
    if VOICE_AVAILABLE:
        voice_enabled = st.toggle("🔊 Voice Output", value=True)
    else:
        voice_enabled = False
    
    st.caption(f"📊 {len(chats)} conversations")

# ============================================
# DISPLAY MESSAGES
# ============================================

current_chats = load_all_chats()
if st.session_state.current_chat_id in current_chats:
    st.markdown(f"### {current_chats[st.session_state.current_chat_id]['name']}")

# Display all messages with proper image rendering
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        # Check if this message has an image
        if msg.get("image"):
            st.image(msg["image"], width=400)
        else:
            # Check if content is a dict with type image
            if isinstance(msg.get("content"), dict) and msg["content"].get("type") == "image":
                st.image(msg["content"]["content"], width=400)
            else:
                st.markdown(msg.get("content", ""))

# ============================================
# USER INPUT
# ============================================

user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    add_message_to_chat(st.session_state.current_chat_id, "user", user_input)
    
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
    
    # Process AI response
    with st.chat_message("assistant", avatar="🤖"):
        with st.status("🤔 Thinking...", expanded=False) as status:
            status.update(label="🔄 Processing...", state="running")
            
            # Get memory and context
            memory_response = extract_user_info(user_input, "")
            enhanced_prompt = get_personalized_context(user_input)
            task = detect_task(user_input)
            
            # ============================================
            # TEXT TASK
            # ============================================
            if task == "text":
                from tools.text_tools import ask_autonomous
                response = ask_autonomous(enhanced_prompt)
                if memory_response:
                    response = f"{memory_response}\n\n{response}"
                
                status.update(label="✨ Complete!", state="complete")
                st.markdown(response)
                
                # Save to session and chat
                st.session_state.messages.append({"role": "assistant", "content": response})
                add_message_to_chat(st.session_state.current_chat_id, "assistant", response)
                
                # Voice output
                if voice_enabled and VOICE_AVAILABLE:
                    speak_text(response[:300])
            
            # ============================================
            # IMAGE TASK
            # ============================================
            elif task == "image":
                from tools.image_tools import flux_image
                
                # Generate image URL
                image_url = flux_image(user_input)
                
                status.update(label="✨ Image generated!", state="complete")
                
                # Display the image
                st.image(image_url, width=400)
                st.caption(f"🎨 Generated for: {user_input}")
                
                # Store in session (as dict with image URL)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"🎨 Generated image for: {user_input}",
                    "image": image_url
                })
                add_message_to_chat(
                    st.session_state.current_chat_id, 
                    "assistant", 
                    f"🎨 Generated image for: {user_input}",
                    image=image_url
                )
                
                # Voice output
                if voice_enabled and VOICE_AVAILABLE:
                    speak_text("Image generated successfully")
            
            # ============================================
            # OTHER TASKS (Video, etc.)
            # ============================================
            else:
                response = execute_task(task, user_input)
                status.update(label="✨ Complete!", state="complete")
                st.markdown(str(response))
                st.session_state.messages.append({"role": "assistant", "content": str(response)})
                add_message_to_chat(st.session_state.current_chat_id, "assistant", str(response))
                
                if voice_enabled and VOICE_AVAILABLE:
                    speak_text(str(response)[:300])

# ============================================
# SAVE CHAT HISTORY
# ============================================

# Auto-save happens in add_message_to_chat function