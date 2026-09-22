import pandas as pd
import duckdb

def get_kpis(dataframes):
    kpis = {
        "total_revenue": 0.0,
        "total_orders": 0,
        "active_customers": 0,
        "avg_order_value": 0.0,
        "repeat_purchase_rate": 0.0,
        "churn_risk_avg": 0.0
    }
    
    orders = dataframes.get("orders")
    customers = dataframes.get("customers")
    
    if orders is not None and not orders.empty:
        kpis["total_orders"] = len(orders)
        
        if 'basket_value' in orders.columns:
            kpis["total_revenue"] = float(orders['basket_value'].sum())
            
        if kpis["total_orders"] > 0:
            kpis["avg_order_value"] = kpis["total_revenue"] / kpis["total_orders"]
            
        if 'repeat_purchase_30d' in orders.columns:
            # percentage of orders with repeat_purchase_30d = 1
            repeat_orders = orders['repeat_purchase_30d'].sum()
            kpis["repeat_purchase_rate"] = float((repeat_orders / kpis["total_orders"]) * 100)
            
    if customers is not None and not customers.empty:
        kpis["active_customers"] = len(customers)
        if 'churn_risk_profile' in customers.columns:
            high_churn = len(customers[customers['churn_risk_profile'].astype(str).str.contains('High', case=False, na=False)])
            kpis["churn_risk_avg"] = (high_churn / kpis["active_customers"]) * 100 if kpis["active_customers"] > 0 else 0.0

    return kpis

def format_currency(value):
    if value >= 1_000_000_000:
        return f"₹{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"
    elif value >= 100_000:
        return f"₹{value / 1_000:.1f}K"
    return f"₹{value:,.2f}"

def format_number(value):
    if isinstance(value, float):
        return f"{value:,.1f}"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 100_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,}"

def apply_global_filters(dataframes, filters):
    """
    Applies filters (like City, Persona, etc.) to the raw DataFrames using Pandas.
    Returns a new dict of filtered DataFrames.
    """
    filtered = {}
    for name, df in dataframes.items():
        if df.empty:
            filtered[name] = df
            continue
            
        f_df = df.copy()
        
        # Apply City filter (assuming orders and customers have 'city')
        if filters.get("city") and "city" in f_df.columns:
            if filters["city"] != "All":
                f_df = f_df[f_df["city"] == filters["city"]]
                
        # Apply Persona filter (only on customers for now, or join if needed)
        if filters.get("persona") and "persona" in f_df.columns:
            if filters["persona"] != "All":
                f_df = f_df[f_df["persona"] == filters["persona"]]
                
        filtered[name] = f_df
        
    return filtered

def generate_management_briefing(dataframes, role="Business Head"):
    briefing = {
        "needs_attention": "No critical alerts found.",
        "watch": "Keep an eye on generic trends.",
        "positive": "Overall operations are stable.",
        "priority": "Continue executing on current plan."
    }
    con = duckdb.connect(database=':memory:')
    for name, df in dataframes.items():
        con.register(name, df)
    try:
        if "customers" in dataframes and "orders" in dataframes:
            try:
                high_churn = con.execute("SELECT city, COUNT(*) as c FROM customers WHERE churn_risk_profile ILIKE '%High%' GROUP BY city ORDER BY c DESC LIMIT 1").fetchone()
                if high_churn: briefing["needs_attention"] = f"Customer churn risk is elevated in {high_churn[0]}."
            except: pass
            
            try:
                low_rep = con.execute("SELECT city, AVG(repeat_purchase_30d) as r FROM orders GROUP BY city ORDER BY r ASC LIMIT 1").fetchone()
                if low_rep: briefing["watch"] = f"Repeat purchase rates are underperforming in {low_rep[0]}."
            except: pass
            
            try:
                hi_aov = con.execute("SELECT city, AVG(basket_value) as a FROM orders GROUP BY city ORDER BY a DESC LIMIT 1").fetchone()
                if hi_aov: briefing["positive"] = f"Average order value is strong in {hi_aov[0]} at {format_currency(hi_aov[1])}."
            except: pass
    except: pass
    return briefing

def generate_management_report(dataframes):
    kpis = get_kpis(dataframes)
    report = f"""## Executive Summary
SwiftKart AI Management Report. Active customers: {format_number(kpis['active_customers'])}.

## KPI Overview
- **Total Revenue**: {format_currency(kpis['total_revenue'])}
- **Total Orders**: {format_number(kpis['total_orders'])}
- **Average Order Value**: {format_currency(kpis['avg_order_value'])}
- **Repeat Purchase Rate**: {format_number(kpis['repeat_purchase_rate'])}%
- **Avg Churn Risk**: {format_number(kpis['churn_risk_avg'])}%
"""
    return report

def get_dashboard_queries(dataframes, section):
    """
    Runs rapid DuckDB aggregations for various dashboard charts.
    """
    con = duckdb.connect(database=':memory:')
    for name, df in dataframes.items():
        con.register(name, df)
        
    results = {}
    try:
        if section == "executive":
            if "orders" in dataframes:
                try:
                    results["revenue_by_city"] = con.execute("SELECT city, SUM(basket_value) as revenue FROM orders GROUP BY city ORDER BY revenue DESC").df()
                except: pass
                
                try:
                    results["orders_trend"] = con.execute("SELECT CAST(order_timestamp AS DATE) as dt, COUNT(order_id) as orders, SUM(basket_value) as revenue FROM orders GROUP BY CAST(order_timestamp AS DATE) ORDER BY dt").df()
                except: pass
                
                try:
                    results["delivery_vs_sat"] = con.execute("SELECT ROUND(delivery_time_minutes / 10) * 10 as delivery_bucket, AVG(customer_satisfaction_score) as avg_sat FROM orders GROUP BY delivery_bucket ORDER BY delivery_bucket").df()
                except: pass
                
            if "customers" in dataframes:
                try:
                    results["persona_dist"] = con.execute("SELECT persona, COUNT(*) as count FROM customers GROUP BY persona ORDER BY count DESC").df()
                except: pass
                
            if "customers" in dataframes and "orders" in dataframes:
                try:
                    results["churn_by_persona"] = con.execute("SELECT c.persona, AVG(o.churn_risk_score) as avg_churn FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.persona ORDER BY avg_churn DESC").df()
                except: pass
                
            if "products" in dataframes and "order_items" in dataframes:
                try:
                    results["cat_revenue"] = con.execute("SELECT p.category, SUM(oi.final_price) as revenue FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.category ORDER BY revenue DESC").df()
                except: pass
                
    except Exception as e:
        print(f"DuckDB error in get_dashboard_queries: {e}")
        
    return results
