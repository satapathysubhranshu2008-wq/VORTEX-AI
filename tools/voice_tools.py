"""Voice Input & Output Tools - PyAudio Free Version"""

import streamlit as st
import pyttsx3
import threading

def speak_text(text):
    """Convert text to speech"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

def voice_input_button():
    """Voice input using Streamlit's native recorder (no PyAudio)"""
    
    # Use Streamlit's built-in audio recorder
    audio_value = st.audio_input("🎤 Click to record your message", key="mic_audio")
    
    if audio_value:
        st.success("✅ Voice captured! (Speech-to-text coming soon)")
        st.info("For now, please type your message or use the text input below.")
        return None
    return None