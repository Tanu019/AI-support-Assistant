import streamlit as st
from app.analytics import format_currency, format_number

def render_sidebar_kpis(kpis):
    """
    Renders the KPI widgets in the Streamlit sidebar.
    """
    st.sidebar.markdown("### 📊 Business Overview")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=format_currency(kpis.get("total_revenue", 0))
        )
        st.metric(
            label="Avg Order Value",
            value=format_currency(kpis.get("avg_order_value", 0))
        )
        
    with col2:
        st.metric(
            label="Total Orders",
            value=format_number(kpis.get("total_orders", 0))
        )
        st.metric(
            label="Active Users",
            value=format_number(kpis.get("active_customers", 0))
        )
        
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am SwiftKart AI. What business metrics or customer trends would you like to explore today?", "type": "text"}
        ]
        st.rerun()
    
def render_suggested_prompts():
    """
    Renders some suggested analytical prompts for the user.
    """
    st.markdown("### 💡 Suggested Analytical Queries")
    
    col1, col2 = st.columns(2)
    
    prompts = [
        "Which city has the highest repeat purchases?",
        "What factors affect customer satisfaction?",
        "Which customers are highly coupon dependent?",
        "What drives churn risk based on demographics?"
    ]
    
    with col1:
        if st.button(prompts[0], use_container_width=True):
            return prompts[0]
        if st.button(prompts[1], use_container_width=True):
            return prompts[1]
            
    with col2:
        if st.button(prompts[2], use_container_width=True):
            return prompts[2]
        if st.button(prompts[3], use_container_width=True):
            return prompts[3]
            
    return None

def inject_whatsapp_css():
    st.markdown("""
    <style>
        /* Chat background */
        .stApp {
            background-color: #0b141a;
        }
        
        /* Chat Input */
        .stChatInputContainer {
            background-color: #202c33;
            border-color: #202c33;
        }
        
        /* Custom Message Bubbles */
        .wa-message-container {
            display: flex;
            margin-bottom: 12px;
            width: 100%;
        }
        
        .wa-message-container.user {
            justify-content: flex-end;
        }
        
        .wa-message-container.assistant {
            justify-content: flex-start;
        }
        
        .wa-bubble {
            max-width: 75%;
            padding: 8px 12px;
            border-radius: 7.5px;
            font-size: 15px;
            line-height: 1.4;
            color: #e9edef;
            box-shadow: 0 1px 0.5px rgba(11,20,26,.13);
            position: relative;
        }
        
        .wa-message-container.user .wa-bubble {
            background-color: #005c4b;
            border-top-right-radius: 0;
        }
        
        .wa-message-container.assistant .wa-bubble {
            background-color: #202c33;
            border-top-left-radius: 0;
        }
        
        /* Time text (mock) */
        .wa-time {
            font-size: 11px;
            color: rgba(255,255,255,0.6);
            float: right;
            margin-top: 8px;
            margin-left: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

def initialize_chat_history():
    """
    Initializes the session state for chat history.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am SwiftKart AI. What business metrics or customer trends would you like to explore today?", "type": "text"}
        ]

def render_message_bubble(role, content_text):
    """
    Renders a single text message as a WhatsApp-style bubble using HTML.
    """
    if role == "user":
        html = f"""
        <div class="wa-message-container user">
            <div class="wa-bubble">
                {content_text}
                <span class="wa-time">now</span>
            </div>
        </div>
        """
    else:
        import html as html_lib
        safe_content = html_lib.escape(content_text).replace('\\n', '<br>')
        import re
        safe_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe_content)
        
        html = f"""
        <div class="wa-message-container assistant">
            <div class="wa-bubble">
                {safe_content}
                <span class="wa-time">now</span>
            </div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)

def render_chat_history():
    """
    Displays the chat history, handling text, dataframes, and charts.
    """
    for message in st.session_state.messages:
        msg_type = message.get("type", "text")
        
        if msg_type == "text":
            render_message_bubble(message["role"], message["content"])
            
        elif msg_type == "table":
            render_message_bubble(message["role"], "Here is the data table you requested:")
            
            # Restrict width to 75% to match chat bubbles
            col1, col2 = st.columns([3, 1])
            with col1:
                st.dataframe(message["content"], use_container_width=True, hide_index=True)
                # Add download button
                csv = message["content"].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="swiftkart_data.csv",
                    mime="text/csv",
                    key=f"dl_{id(message)}" # unique key
                )
            
        elif msg_type == "chart":
            render_message_bubble(message["role"], "Here is the visualization:")
            
            # Restrict width to 75% to match chat bubbles
            col1, col2 = st.columns([3, 1])
            with col1:
                st.plotly_chart(message["content"], use_container_width=True)
