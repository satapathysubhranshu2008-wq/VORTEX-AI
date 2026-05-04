"""Web Search Tools - Free via DuckDuckGo"""

import streamlit as st
from duckduckgo_search import DDGS

def web_search(query, max_results=3):
    """
    Search the web using DuckDuckGo (completely free, no API key)
    Returns formatted results with titles, links, and snippets
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return "No results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            body = result.get('body', 'No description')
            href = result.get('href', '#')
            
            formatted.append(f"**{i}. {title}**\n{body}\n🔗 [Link]({href})\n")
        
        return "\n".join(formatted)
        
    except Exception as e:
        return f"Search error: {str(e)}"

def search_and_summarize(query, agent):
    """
    Search the web and let the AI summarize the results
    """
    search_results = web_search(query, max_results=3)
    
    if search_results.startswith("Search error") or search_results == "No results found.":
        return search_results
    
    # Create prompt for AI to summarize
    summarization_prompt = f"""
You are a helpful assistant. A user asked: "{query}"

Here are search results from the web:
{search_results}

Please provide a clear, concise answer to the user's question based on these search results.
Cite your sources by referring to the links. Keep it under 200 words.
"""
    
    # Use your existing AI to summarize
    from tools.text_tools import ask_autonomous
    summary = ask_autonomous(summarization_prompt)
    
    return f"🔍 **Web Search Results for:** '{query}'\n\n{summary}\n\n---\n*Sources:*\n{search_results}"