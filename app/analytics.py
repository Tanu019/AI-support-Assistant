import pandas as pd

def get_kpis(dataframes):
    """
    Calculates high-level KPIs for the sidebar or main dashboard.
    """
    kpis = {
        "total_revenue": 0,
        "total_orders": 0,
        "active_customers": 0,
        "avg_order_value": 0
    }
    
    orders = dataframes.get("orders")
    order_items = dataframes.get("order_items")
    customers = dataframes.get("customers")
    
    if orders is not None and not orders.empty:
        kpis["total_orders"] = len(orders)
        
        # Check if 'basket_value' is in orders, or calculate from order_items
        if 'basket_value' in orders.columns:
            kpis["total_revenue"] = orders['basket_value'].sum()
        elif 'total_amount' in orders.columns:
            kpis["total_revenue"] = orders['total_amount'].sum()
        elif order_items is not None and not order_items.empty and 'final_price' in order_items.columns:
            kpis["total_revenue"] = order_items['final_price'].sum()
            
        if kpis["total_orders"] > 0:
            kpis["avg_order_value"] = kpis["total_revenue"] / kpis["total_orders"]
            
    if customers is not None and not customers.empty:
        kpis["active_customers"] = len(customers)
        
    return kpis

def format_currency(value):
    if value >= 1_000_000_000:
        return f"₹{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"₹{value / 1_000_000:.1f}M"
    elif value >= 100_000: # Abbreviate above 100k
        return f"₹{value / 1_000:.1f}K"
    return f"₹{value:,.2f}"

def format_number(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 100_000: # Abbreviate above 100k
        return f"{value / 1_000:.1f}K"
    return f"{value:,}"
