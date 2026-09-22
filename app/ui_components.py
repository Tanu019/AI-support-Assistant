import streamlit as st
from app.analytics import format_currency, format_number
from app.visualizations import (
    plot_revenue_by_city, plot_orders_trend, plot_persona_dist,
    plot_delivery_vs_sat, plot_churn_by_persona, plot_cat_revenue
)

def inject_enterprise_css(theme):
    if theme == "Light":
        bg_color = "#eef0e5"
        sidebar_bg = "#e4e6d9"
        text_color = "#2c3329"
        card_bg = "#ffffff"
        border_color = "rgba(44, 51, 41, 0.05)"
        shadow_hover = "rgba(44, 51, 41, 0.08)"
        user_bubble = "#e4e6d9"
        assistant_bubble = "#ffffff"
        kpi_value_color = "#1a201b"
        chat_input_bg = "#ffffff"
        chat_border = "rgba(44, 51, 41, 0.1)"
        accent_button = "#dcf294"
        accent_button_hover = "#d0e685"
    else: # Dark
        bg_color = "#1a201b"
        sidebar_bg = "#141915"
        text_color = "#eef0e5"
        card_bg = "#232b25"
        border_color = "rgba(238, 240, 229, 0.05)"
        shadow_hover = "rgba(238, 240, 229, 0.1)"
        user_bubble = "#3a4a3f"
        assistant_bubble = "#232b25"
        kpi_value_color = "#ffffff"
        chat_input_bg = "#232b25"
        chat_border = "rgba(238, 240, 229, 0.1)"
        accent_button = "#3a4a3f"
        accent_button_hover = "#4a5d4e"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&display=swap');
        
        /* Global */
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {text_color} !important; }}
        
        /* App and Layout */
        .stApp {{ background-color: {bg_color}; }}
        .block-container {{ padding-top: 2rem !important; }}
        [data-testid="stHeader"] {{ background-color: transparent !important; }}
        
        /* Sidebar Fixes */
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid {border_color}; }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .st-emotion-cache-1wmy9hl {{ color: {text_color} !important; }}
        
        /* Selectboxes (Dropdowns) */
        div[data-baseweb="select"] > div {{
            background-color: {card_bg} !important;
            border: 1px solid {border_color} !important;
            color: {text_color} !important;
            border-radius: 8px;
        }}
        
        /* Headers */
        h1, h2, h3, .chart-header {{ font-family: 'Playfair Display', serif !important; color: {kpi_value_color} !important; font-weight: 500 !important; }}
        
        .stChatInputContainer {{ background-color: {chat_input_bg}; border-color: {chat_border}; box-shadow: 0 -4px 10px rgba(0,0,0,0.02); border-radius: 20px; }}
        
        /* Chat */
        .enterprise-message-container {{ display: flex; margin-bottom: 20px; width: 100%; }}
        .enterprise-message-container.user {{ justify-content: flex-end; }}
        .enterprise-message-container.assistant {{ justify-content: flex-start; }}
        .enterprise-bubble {{ max-width: 80%; padding: 18px 24px; border-radius: 16px; font-size: 15.5px; line-height: 1.6; color: {text_color}; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03); }}
        .enterprise-message-container.user .enterprise-bubble {{ background-color: {user_bubble}; border-bottom-right-radius: 4px; }}
        .enterprise-message-container.assistant .enterprise-bubble {{ background-color: {assistant_bubble}; border-bottom-left-radius: 4px; border: 1px solid {border_color}; }}
        .enterprise-bubble h3 {{ margin-top: 0; margin-bottom: 8px; font-size: 18px; color: {kpi_value_color}; font-weight: 500; font-family: 'Playfair Display', serif; }}
        
        /* Dashboard KPI Cards */
        .kpi-card {{ 
            background: {card_bg}; 
            padding: 24px; 
            border-radius: 16px; 
            text-align: left; 
            border: 1px solid {border_color};
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.02);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 35px {shadow_hover};
        }}
        .kpi-value {{ font-size: 32px; font-weight: 400; color: {kpi_value_color}; margin: 16px 0 0 0; letter-spacing: -0.2px; font-family: 'Playfair Display', serif; }}
        .kpi-label {{ font-size: 13px; font-weight: 500; color: {text_color}; opacity: 0.7; text-transform: uppercase; letter-spacing: 1px; }}
        
        .kpi-icon {{ font-size: 22px; color: {text_color}; opacity: 0.8; background: {bg_color}; padding: 8px; border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; }}
        
        /* Premium Streamlit Buttons */
        div.stButton > button {{
            background: {accent_button} !important;
            color: #2c3329 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
        }}
        div.stButton > button:hover {{
            background: {accent_button_hover} !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.06) !important;
            transform: translateY(-2px) !important;
        }}
        
        /* Custom header column for charts */
        .chart-header {{
            margin-top: 10px;
            margin-bottom: 10px;
            font-size: 20px;
            font-weight: 500;
        }}
    </style>
    """, unsafe_allow_html=True)



def render_kpi_card(title, value, icon, icon_class):
    return f"""
    <div class='kpi-card'>
        <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
            <div class='kpi-label'>{title}</div>
            <div class='kpi-icon {icon_class}'>{icon}</div>
        </div>
        <div class='kpi-value'>{value}</div>
    </div>
    """

def render_kpi_row(kpis):
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(render_kpi_card("Total Revenue", format_currency(kpis.get('total_revenue', 0)), "💰", "blue"), unsafe_allow_html=True)
    with c2: st.markdown(render_kpi_card("Total Orders", format_number(kpis.get('total_orders', 0)), "📦", "green"), unsafe_allow_html=True)
    with c3: st.markdown(render_kpi_card("Avg Order Value", format_currency(kpis.get('avg_order_value', 0)), "🛒", "purple"), unsafe_allow_html=True)
    with c4: st.markdown(render_kpi_card("Active Customers", format_number(kpis.get('active_customers', 0)), "👥", "blue"), unsafe_allow_html=True)

def render_kpi_row_2(kpis):
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(render_kpi_card("Repeat Purchase Rate", f"{kpis.get('repeat_purchase_rate', 0):.1f}%", "🔁", "green"), unsafe_allow_html=True)
    with c2: st.markdown(render_kpi_card("Avg Churn Risk", f"{kpis.get('churn_risk_avg', 0):.1f}%", "⚠️", ""), unsafe_allow_html=True)
    with c3: st.markdown(render_kpi_card("Customer Satisfaction", "4.2 / 5", "⭐", "purple"), unsafe_allow_html=True)

def handle_explain_with_ai(prompt):
    st.session_state.pending_ai_query = prompt
    st.session_state.current_page = "🤖 Chatbot"
    st.rerun()

def render_chart_section(title, fig, button_text, explain_prompt, key):
    hc, bc = st.columns([0.65, 0.35])
    with hc:
        # Added padding-top to perfectly align the title with the button next to it
        st.markdown(f"<div class='chart-header' style='margin:0; padding-top:12px;'>{title}</div>", unsafe_allow_html=True)
    with bc:
        if st.button(button_text, key=key, use_container_width=True): 
            handle_explain_with_ai(explain_prompt)
    if fig: 
        st.plotly_chart(fig, use_container_width=True)

def render_executive_overview(kpis, briefing, charts_data):
    st.markdown("""
        <div style="text-align: left; margin-bottom: 2rem; padding-top: 1rem;">
            <h1 style="font-family: 'Playfair Display', serif; font-size: 3.2rem; margin-bottom: 0.2rem; font-weight: 400; letter-spacing: -0.5px;">SwiftKart Intelligence</h1>
            <p style="font-family: 'Inter', sans-serif; font-size: 1.05rem; opacity: 0.6; font-weight: 300;">Smart Assistant for Enterprise Analytics</p>
        </div>
    """, unsafe_allow_html=True)
    
    render_kpi_row(kpis)
    st.markdown("<br>", unsafe_allow_html=True)
    render_kpi_row_2(kpis)
    
    st.markdown("---")
    st.subheader("🔎 Management Alerts")
    c1, c2 = st.columns(2)
    with c1:
        st.error(f"🔴 **Needs Attention**: {briefing['needs_attention']}")
        st.success(f"🟢 **Positive**: {briefing['positive']}")
    with c2:
        st.warning(f"🟡 **Watch**: {briefing['watch']}")
        st.info(f"🔵 **Opportunity**: {briefing['priority']}")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        render_chart_section("Revenue by City", plot_revenue_by_city(charts_data.get("revenue_by_city")), "✨ Explain with AI", "Why is revenue distributed like this across cities?", "exp_rev_city")
            
    with c2:
        render_chart_section("Order Trends", plot_orders_trend(charts_data.get("orders_trend")), "✨ Explain with AI", "What is causing the current trend in orders over time?", "exp_ord_trend")

    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3:
        render_chart_section("Customer Personas", plot_persona_dist(charts_data.get("persona_dist")), "✨ Explain with AI", "Which customer persona is the most valuable and why?", "exp_personas")
    with c4:
        render_chart_section("Avg Churn Risk by Persona", plot_churn_by_persona(charts_data.get("churn_by_persona")), "✨ Explain with AI", "Why does this persona have a higher churn risk?", "exp_churn_persona")
        
    st.markdown("---")
    c5, c6 = st.columns(2)
    with c5:
        render_chart_section("Delivery vs Satisfaction", plot_delivery_vs_sat(charts_data.get("delivery_vs_sat")), "✨ Explain with AI", "Does delivery time impact customer satisfaction in our data?", "exp_delivery_sat")
    with c6:
        render_chart_section("Category Revenue", plot_cat_revenue(charts_data.get("cat_revenue")), "✨ Explain with AI", "Which product category is driving the most revenue?", "exp_cat_rev")

    # Animated Floating Action Button for Chatbot
    if st.button("✦", key="chatbot_fab", help="Open Chatbot Assistant"):
        st.session_state.current_page = "🤖 Chatbot"
        st.rerun()

    # Robust JS injection to style the button and move it to the bottom right
    import streamlit.components.v1 as components
    components.html("""
        <style>
        @keyframes pulse-glow {
            0% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.8); }
            50% { box-shadow: 0 0 0 25px rgba(139, 92, 246, 0); }
            100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0); }
        }
        @keyframes float-bob {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
            100% { transform: translateY(0px); }
        }
        @keyframes sparkle-spin {
            0% { transform: rotate(0deg) scale(1); }
            50% { transform: rotate(180deg) scale(1.2); }
            100% { transform: rotate(360deg) scale(1); }
        }
        </style>
        <script>
        const doc = window.parent.document;
        
        function styleFab() {
            // Find the button containing exactly the ✦ or ✨ emoji
            const buttons = Array.from(doc.querySelectorAll('button'));
            const fab = buttons.find(b => b.innerText.trim() === '✦' || b.innerText.trim() === '✨' || b.innerText.trim() === '🤖');
            
            if (fab) {
                // Find its outermost Streamlit element container
                const container = fab.closest('div[data-testid="stElementContainer"]') || fab.parentElement;
                
                if (container && container.style.position !== 'fixed') {
                    // Float the container to the bottom right
                    container.style.position = 'fixed';
                    container.style.bottom = '40px';
                    container.style.right = '40px';
                    container.style.zIndex = '999999';
                    
                    // The container bobs up and down
                    container.style.animation = 'float-bob 3s ease-in-out infinite';
                    
                    // Style the button to be a beautiful glowing orb
                    fab.style.width = '75px';
                    fab.style.height = '75px';
                    fab.style.borderRadius = '50%';
                    fab.style.fontSize = '40px';
                    fab.style.display = 'flex';
                    fab.style.alignItems = 'center';
                    fab.style.justifyContent = 'center';
                    fab.style.padding = '0';
                    fab.style.background = 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)';
                    fab.style.border = 'none';
                    fab.style.color = 'white';
                    fab.style.animation = 'pulse-glow 2s infinite';
                    fab.style.boxShadow = '0 6px 20px rgba(139, 92, 246, 0.6)';
                    fab.style.cursor = 'pointer';
                    fab.style.textShadow = '0 0 10px rgba(255,255,255,0.8)';
                    
                    // Add an internal spinning animation to the text/icon inside the button
                    const p = fab.querySelector('p');
                    if (p) {
                        p.style.animation = 'sparkle-spin 4s linear infinite';
                        p.style.display = 'inline-block';
                    }
                }
            }
        }
        
        // Run immediately and repeatedly to prevent Streamlit from wiping the styles on rerun
        styleFab();
        setInterval(styleFab, 200);
        </script>
    """, height=0)

# --- Chat Components (Reused & Updated) ---

def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI Management Analyst. What would you like to explore?", "type": "text"}]
    if "follow_ups" not in st.session_state:
        st.session_state.follow_ups = [
            "Which city has the highest revenue?",
            "Which customer segment has the highest churn risk?",
            "Which products have high revenue but low margins?",
            "Does delivery time impact customer satisfaction?"
        ]

def render_message_bubble(role, content_text):
    if role == "user":
        html = f"<div class='enterprise-message-container user'><div class='enterprise-bubble'>{content_text}</div></div>"
    else:
        import html as html_lib
        import re
        safe_content = html_lib.escape(content_text).replace('\n', '<br>')
        safe_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe_content)
        safe_content = re.sub(r'### (.*?)(<br>|$)', r'<h3>\1</h3>\2', safe_content)
        html = f"<div class='enterprise-message-container assistant'><div class='enterprise-bubble'>{safe_content}</div></div>"
    st.markdown(html, unsafe_allow_html=True)

def render_follow_ups():
    if st.session_state.follow_ups:
        st.markdown("### Explore Further")
        cols = st.columns(len(st.session_state.follow_ups))
        for idx, q in enumerate(st.session_state.follow_ups):
            with cols[idx]:
                if st.button(q, key=f"fu_{idx}", use_container_width=True):
                    st.session_state.follow_ups = []
                    return q
    return None

def render_chat_history():
    for message in st.session_state.messages:
        msg_type = message.get("type", "text")
        if msg_type == "text":
            render_message_bubble(message["role"], message["content"])
        elif msg_type == "table":
            render_message_bubble(message["role"], "Here is the data table you requested:")
            st.dataframe(message["content"], use_container_width=True, hide_index=True)
        elif msg_type == "chart":
            render_message_bubble(message["role"], "Here is the visualization:")
            st.plotly_chart(message["content"], use_container_width=True)

def render_data_used(dataframes):
    st.sidebar.markdown("### 🗄️ Data Coverage")
    if 'customers' in dataframes: st.sidebar.caption(f"• **{len(dataframes['customers']):,}** Customers")
    if 'orders' in dataframes: st.sidebar.caption(f"• **{len(dataframes['orders']):,}** Orders")
    if 'products' in dataframes: st.sidebar.caption(f"• **{len(dataframes['products']):,}** Products")
    if 'order_items' in dataframes: st.sidebar.caption(f"• **{len(dataframes['order_items']):,}** Order Items")
