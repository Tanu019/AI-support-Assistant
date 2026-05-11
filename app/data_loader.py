import pandas as pd
import streamlit as st
import os

@st.cache_resource
def load_data():
    """
    Loads all required CSV datasets into pandas DataFrames.
    Uses Streamlit caching to prevent reloading data on every interaction.
    """
    data_dir = "data"
    
    # Define file paths
    files = {
        "customers": os.path.join(data_dir, "customers.csv"),
        "products": os.path.join(data_dir, "products.csv"),
        "orders": os.path.join(data_dir, "orders.csv"),
        "order_items": os.path.join(data_dir, "order_items.csv")
    }
    
    dataframes = {}
    
    try:
        dataframes["customers"] = pd.read_csv(files["customers"])
    except FileNotFoundError:
        st.warning("customers.csv not found.")
        dataframes["customers"] = pd.DataFrame()
        
    try:
        dataframes["products"] = pd.read_csv(files["products"])
    except FileNotFoundError:
        st.warning("products.csv not found.")
        dataframes["products"] = pd.DataFrame()
        
    try:
        dataframes["orders"] = pd.read_csv(files["orders"])
    except FileNotFoundError:
        st.warning("orders.csv not found.")
        dataframes["orders"] = pd.DataFrame()
        
    try:
        dataframes["order_items"] = pd.read_csv(files["order_items"])
    except FileNotFoundError:
        st.warning("order_items.csv not found.")
        dataframes["order_items"] = pd.DataFrame()
        
    return dataframes
