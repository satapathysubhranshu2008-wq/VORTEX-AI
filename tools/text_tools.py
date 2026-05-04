"""Text AI with autonomous discovery"""

import streamlit as st
from tools.discovery import select_best_model, execute_with_model

def ask_autonomous(prompt):
    """
    Automatically discovers and uses the best free model.
    No hardcoding. No config.json for models.
    """
    # Step 1: Discover best model for this task
    best_model = select_best_model(prompt, task_type="text")
    
    if not best_model:
        return "No free models available right now. Please try again later."
    
    # Step 2: Execute with discovered model
    return execute_with_model(best_model, prompt)
def ask_with_web_search(prompt):
    """
    Automatically detects if web search is needed and uses it
    """
    prompt_lower = prompt.lower()
    
    # Keywords that suggest web search is needed
    search_keywords = [
        "latest", "news", "today", "yesterday", "current", 
        "weather", "score", "result", "who won", "what is the",
        "find", "search", "tell me about", "update"
    ]
    
    needs_search = any(keyword in prompt_lower for keyword in search_keywords)
    
    if needs_search:
        from tools.search_tools import search_and_summarize
        return search_and_summarize(prompt, None)
    else:
        # Use normal autonomous AI
        from tools.discovery import select_best_model, execute_with_model
        best_model = select_best_model(prompt, "text")
        if best_model:
            return execute_with_model(best_model, prompt)
        return "No model available"
TEXT_MODELS = {
    "autonomous": ask_with_web_search,  # This uses web search when needed
}