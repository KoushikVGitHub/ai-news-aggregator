import streamlit as st
import requests

# --- CONFIGURATION ---
BACKEND_URL = "http://backend:8000" # URL of FastAPI backend

st.set_page_config(page_title="AI News Aggregator", layout="wide")

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=600) # Cache data for 10 minutes
def fetch_highlights():
    """Fetches highlight data from the backend API."""
    try:
        response = requests.get(f"{BACKEND_URL}/highlights")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the backend: {e}")
        return None

def ask_chatbot(question):
    """Sends a question to the chatbot backend and gets an answer."""
    try:
        response = requests.post(f"{BACKEND_URL}/chatbot/ask", json={"question": question})
        response.raise_for_status()
        return response.json()["answer"]
    except requests.exceptions.RequestException as e:
        return f"Error communicating with chatbot: {e}"

# --- MAIN UI ---
st.title("Australian News Highlights and Chatbot Interface")

highlights_data = fetch_highlights()

if highlights_data:
    # Create tabs for each category
    capitalized_tabs = [cat.capitalize() for cat in highlights_data.keys()]
    category_tabs = st.tabs(capitalized_tabs)

    for i, (category, articles) in enumerate(highlights_data.items()):
        with category_tabs[i]:
            if not articles:
                st.write(f"No recent articles found for {category}.")
                continue
            
            for article in articles:
                with st.container():
                    if article.get("image_url"):
                        st.image(article["image_url"])
                    
                    st.subheader(article["title"])
                    
                    authors_raw = article.get("authors", "N/A")

                    # Clean the string if it's not a proper list
                    if isinstance(authors_raw, str):
                        # Remove brackets, quotes, and split by comma
                        cleaned_authors = authors_raw.strip("[]").replace("'", "").replace('"', '')
                        authors = cleaned_authors if cleaned_authors else "N/A"
                    else:
                        # If it's already a list, join it
                        authors = ", ".join(authors_raw) if authors_raw else "N/A"
                    st.markdown(f"**Source:** `{article.get('source', 'N/A')}` | **Authors:** `{authors}`")
                    
                    st.write(article.get("summary", "No summary available."))
                    
                    with st.expander("Show Full Text"):
                        st.write(article.get("full_text", "No full text available."))

# --- CHATBOT INTERFACE ---
st.sidebar.header("Chat with the News")
user_question = st.sidebar.text_input("Ask a question about today's highlights:", key="chat_input")

if st.sidebar.button("Ask", key="ask_button"):
    if user_question:
        with st.sidebar:
            with st.spinner("Thinking..."):
                answer = ask_chatbot(user_question)
                st.info(answer)
    else:
        st.sidebar.warning("Please enter a question.")