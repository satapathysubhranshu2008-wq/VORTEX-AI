"""Image Generation - Multiple Fallback Methods"""

import requests
import streamlit as st
from datetime import datetime
import base64

def flux_image(prompt):
    """Generate image using Pollinations with fallback"""
    
    # Encode prompt for URL
    encoded = requests.utils.quote(prompt)
    
    # Method 1: Direct Pollinations URL
    url = f"https://image.pollinations.ai/prompt/{encoded}"
    
    # Return as markdown image (works more reliably)
    return url

def get_image_html(prompt):
    """Return HTML that forces image to load"""
    encoded = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}"
    
    # Add random timestamp to force reload
    url_with_timestamp = f"{url}&_={int(datetime.now().timestamp())}"
    
    return f'<img src="{url_with_timestamp}" width="500" style="border-radius: 10px; margin: 10px 0;">'

IMAGE_MODELS = {
    "flux": flux_image,
    "get_image_html": get_image_html
}