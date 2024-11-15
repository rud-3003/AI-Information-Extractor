import requests
import streamlit as st

def search_with_serpapi(query):
    """
    Function to perform a web search using SerpAPI.
    Returns the top result with URL, title, and snippet.
    """
    api_key = st.secrets["serpapi"]["api_key"]
    search_url = "https://serpapi.com/search"
    
    params = {
        "q": query,
        "api_key": api_key,
        "engine": "google",
        "num": 3  # Fetch top 3 results
    }
    
    try:
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            results = response.json().get("organic_results", [])
            return results if results else None
        else:
            st.error("Failed to fetch search results.")
            return None
    except Exception as e:
        st.error(f"Error during web search: {e}")
        return None
