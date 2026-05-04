"""Autonomous model discovery - No hardcoded models"""

import requests
import streamlit as st
from datetime import datetime

def discover_free_models():
    """
    Queries OpenRouter registry for available free models.
    Returns list of models with capabilities.
    """
    try:
        url = "https://openrouter.ai/api/v1/models"
        headers = {
            "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        
        # Debug: Print status
        print(f"DEBUG: API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"DEBUG: Error Response: {response.text[:200]}")
            return []
        
        data = response.json()
        
        # Debug: Check structure
        print(f"DEBUG: Response contains 'data': {'data' in data}")
        
        models = data.get("data", [])
        print(f"DEBUG: Total models from API: {len(models)}")
        
        # Filter free models (pricing.prompt = 0)
        free_models = []
        for model in models:
            # Check different possible pricing structures
            pricing = model.get("pricing", {})
            prompt_price = pricing.get("prompt", 1)  # Default to 1 if not found
            
            # Also check if it's free via description
            is_free = False
            if prompt_price == 0:
                is_free = True
            elif "free" in model.get("description", "").lower():
                is_free = True
            elif model.get("id", "").endswith("-free"):
                is_free = True
            
            if is_free:
                free_models.append({
                    "id": model.get("id", "unknown"),
                    "name": model.get("name", "Unknown"),
                    "provider": model.get("provider", {}).get("name", "Unknown"),
                    "description": model.get("description", "")[:200],
                    "context_length": model.get("context_length"),
                    "pricing": pricing
                })
        
        print(f"DEBUG: Found {len(free_models)} free models")
        if len(free_models) > 0:
            print(f"DEBUG: First free model: {free_models[0]['name']}")
        
        return free_models
        
    except Exception as e:
        print(f"DEBUG: Exception: {e}")
        return []

def select_best_model(prompt, task_type="text"):
    """
    Automatically selects the best model for the task.
    """
    models = discover_free_models()
    
    if not models or not isinstance(models, list) or len(models) == 0:
        print("DEBUG: No free models available")
        return None
    
    # Simple selection: pick first available
    # For now, just return the first free model's ID
    best_model_id = models[0]["id"]
    print(f"DEBUG: Selected model: {best_model_id}")
    return best_model_id

def execute_with_model(model_id, prompt):
    """
    Execute a task using a specific model ID from OpenRouter.
    """
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Autonomous AI Agent"
        }
        data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        print(f"DEBUG: Executing with model: {model_id}")
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: {result.get('error', {}).get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"Error: {e}"