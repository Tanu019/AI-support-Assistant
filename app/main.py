import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv

# Set page configuration must be the first Streamlit command
st.set_page_config(
    page_title="SwiftKart AI | Enterprise Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

from app.data_loader import load_data
from app.analytics import get_kpis
from app.ui_components import (
    render_sidebar_kpis, 
    render_suggested_prompts, 
    initialize_chat_history, 
    render_chat_history,
    inject_whatsapp_css,
    render_message_bubble
)
from app.chat_engine import init_chat_engine, ask_assistant

# Load environment variables (OPENAI_API_KEY)
load_dotenv()

@st.cache_resource
def get_cached_data():
    return load_data()

@st.cache_resource
def get_cached_engine(_dataframes):
    # Cache busted again to load sample rows logic
    return init_chat_engine(_dataframes)

def main():
    st.title("🛒 SwiftKart AI - Consumer Insights Analyst")
    st.markdown("Welcome to the enterprise analytics chatbot. Ask me anything about our customers, orders, or product performance.")
    
    # Inject WhatsApp Theme
    inject_whatsapp_css()
    
    # 1. Load Data (Cached)
    with st.spinner("Loading Enterprise Data Datalake..."):
        dataframes = get_cached_data()
        
    # 2. Calculate and Render KPIs
    kpis = get_kpis(dataframes)
    render_sidebar_kpis(kpis)
    
    # 3. Initialize Chat Engine (Cached)
    datalake = get_cached_engine(dataframes)
    
    if not datalake:
        st.stop() # Stop execution if chat engine fails (e.g. no API key)
        
    # 4. Initialize UI Components
    initialize_chat_history()
    
    # Suggest prompts (returns a string if a button is clicked)
    suggested_prompt = render_suggested_prompts()
    
    st.markdown("---")
    
    # 5. Render Chat History
    render_chat_history()
    
    # 6. Handle User Input
    user_input = st.chat_input("Ask a business question...")
    prompt = suggested_prompt if suggested_prompt else user_input
    
    if prompt:
        # Append user message to chat history and render
        st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
        st.rerun() # Refresh to show user message immediately while processing

    # Note: Streamlit executes top-to-bottom, so the user message will now be rendered 
    # by render_chat_history() on the next run. We need to handle the assistant response 
    # if the last message was from the user.
    
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_prompt = st.session_state.messages[-1]["content"]
        history = st.session_state.messages[:-1]
        
        # We handle spinners differently now to allow streaming
        with st.spinner("Analyzing datasets..."):
            response = ask_assistant(datalake, last_prompt, history)
            
            import plotly.graph_objects as go
            import types
            
            # Check response type
            if isinstance(response, pd.DataFrame): 
                st.session_state.messages.append({"role": "assistant", "content": response, "type": "table"})
                st.rerun()
            elif isinstance(response, go.Figure):
                st.session_state.messages.append({"role": "assistant", "content": response, "type": "chart"})
                st.rerun()
            elif isinstance(response, types.GeneratorType):
                # Real-time streaming
                placeholder = st.empty()
                full_response = ""
                for chunk in response:
                    full_response += chunk
                    with placeholder.container():
                        render_message_bubble("assistant", full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response, "type": "text"})
            else:
                # Fallback for cached or error strings
                st.session_state.messages.append({"role": "assistant", "content": str(response), "type": "text"})
                st.rerun()

if __name__ == "__main__":
    main()
