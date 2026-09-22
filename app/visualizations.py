import plotly.graph_objects as go
import streamlit as st

def _apply_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1e293b', family='Inter, sans-serif'),
        margin=dict(l=10, r=10, t=50, b=10),
        height=280,
        xaxis=dict(showgrid=False, zeroline=False, color='#64748b'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False, color='#64748b'),
        hovermode='x unified'
    )
    return fig

def plot_revenue_by_city(df):
    if df is None or df.empty:
        return None
    fig = go.Figure(go.Bar(
        x=df['city'],
        y=df['revenue'],
        marker=dict(
            color=df['revenue'],
            colorscale=[[0, '#3b82f6'], [1, '#8b5cf6']],
            showscale=False,
            line=dict(color='rgba(255,255,255,0)', width=0)
        ),
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(title=dict(text="Revenue by City", font=dict(size=18, color="#0f172a")))
    return _apply_theme(fig)

def plot_orders_trend(df):
    if df is None or df.empty:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['dt'], 
        y=df['orders'],
        mode='lines',
        name='Orders',
        line=dict(color='#10b981', width=3, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)',
        hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>'
    ))
    fig.update_layout(title=dict(text="Orders Over Time", font=dict(size=18, color="#0f172a")))
    return _apply_theme(fig)

def plot_persona_dist(df):
    if df is None or df.empty:
        return None
    fig = go.Figure(go.Pie(
        labels=df['persona'],
        values=df['count'],
        hole=0.6,
        marker=dict(colors=['#6366f1', '#ec4899', '#14b8a6', '#f59e0b', '#8b5cf6'],
                    line=dict(color='#ffffff', width=2)),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>%{value} Customers<br>(%{percent})<extra></extra>'
    ))
    fig.update_layout(
        title=dict(text="Customer Personas", font=dict(size=18, color="#0f172a")),
        showlegend=False
    )
    return _apply_theme(fig)

def plot_delivery_vs_sat(df):
    if df is None or df.empty:
        return None
    fig = go.Figure(go.Bar(
        x=df['delivery_bucket'].astype(str) + ' mins',
        y=df['avg_sat'],
        marker_color='#f43f5e',
        hovertemplate='<b>%{x}</b><br>Avg Satisfaction: %{y:.2f}<extra></extra>'
    ))
    fig.update_layout(title=dict(text="Satisfaction by Delivery Time", font=dict(size=18, color="#0f172a")), yaxis=dict(range=[0, 5]))
    return _apply_theme(fig)

def plot_churn_by_persona(df):
    if df is None or df.empty:
        return None
    fig = go.Figure(go.Bar(
        x=df['persona'],
        y=df['avg_churn'],
        marker=dict(
            color=df['avg_churn'],
            colorscale=[[0, '#10b981'], [1, '#ef4444']],
            showscale=False
        ),
        hovertemplate='<b>%{x}</b><br>Avg Churn Risk: %{y:.1f}%<extra></extra>'
    ))
    fig.update_layout(title=dict(text="Avg Churn Risk by Persona", font=dict(size=18, color="#0f172a")))
    return _apply_theme(fig)

def plot_cat_revenue(df):
    if df is None or df.empty:
        return None
    fig = go.Figure(go.Pie(
        labels=df['category'],
        values=df['revenue'],
        hole=0.4,
        marker=dict(colors=['#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6'],
                    line=dict(color='#ffffff', width=2)),
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>(%{percent})<extra></extra>'
    ))
    fig.update_layout(
        title=dict(text="Revenue by Category", font=dict(size=18, color="#0f172a")),
        showlegend=False
    )
    return _apply_theme(fig)
