"""
chat_engine.py
--------------
Uses DuckDB for fast, secure Text-to-SQL querying over pandas DataFrames,
and LlamaIndex for LLM interactions. Supports automatic text synthesis,
raw data table returns, and dynamic Plotly chart generation.
"""

import os
import re
import io
import contextlib
import traceback
import streamlit as st
import pandas as pd
import duckdb
import plotly.graph_objects as go

from llama_index.core.llms import LLM
from llama_index.llms.openai_like import OpenAILike

from app.prompts import SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Groq LLM factory
# ---------------------------------------------------------------------------

def _build_llm() -> OpenAILike | None:
    """Initialise the Groq LLM via the OpenAI-compatible endpoint."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ Please set a valid GROQ_API_KEY in your .env file.")
        return None

    return OpenAILike(
        model="llama-3.3-70b-versatile",
        api_base="https://api.groq.com/openai/v1",
        api_key=api_key,
        is_chat_model=True,
        context_window=8192,
    )


# ---------------------------------------------------------------------------
# Data Schema Definitions
# ---------------------------------------------------------------------------

_DF_DESCRIPTIONS = {
    "customers": (
        "customers — columns: customer_id, persona, age, gender, city, city_tier, "
        "occupation, monthly_income, household_size, loyalty_program_member, "
        "preferred_payment_method, app_engagement_score, price_sensitivity_score, "
        "impulsiveness_score, health_consciousness_score, discount_affinity_score, "
        "late_night_ordering_tendency, weekend_ordering_tendency, brand_loyalty_score, "
        "churn_risk_profile"
    ),
    "products": (
        "products — columns: product_id, category, subcategory, brand, "
        "package_size, mrp, selling_price, margin_percentage, organic_flag, "
        "premium_flag, rating, popularity_index, festival_relevance"
    ),
    "orders": (
        "orders — columns: order_id, customer_id, order_timestamp, delivery_timestamp, "
        "city, weather_condition, festival_flag, payday_period_flag, basket_value, "
        "item_count, discount_amount, delivery_fee, surge_fee, coupon_used, "
        "coupon_type, delivery_time_minutes, packing_delay, stockout_items, "
        "substitution_count, customer_satisfaction_score, refund_requested, "
        "repeat_purchase_7d, repeat_purchase_30d, churn_risk_score, "
        "impulse_purchase_flag, late_night_order_flag, healthy_basket_flag, "
        "premium_basket_flag"
    ),
    "order_items": (
        "order_items — columns: order_item_id, order_id, product_id, "
        "quantity, unit_price, discount, final_price"
    ),
}

# ---------------------------------------------------------------------------
# DuckDB SQL Engine
# ---------------------------------------------------------------------------

class DuckDBEngine:
    """
    A secure text-to-SQL engine using DuckDB.
    1. Translates natural language to SQL.
    2. Executes SQL safely against registered DuckDB tables.
    3. Routes the result to Text, Table, or Chart.
    """

    def __init__(self, dataframes: dict[str, pd.DataFrame], llm: LLM):
        self.llm = llm
        # Initialize an in-memory DuckDB connection
        self.con = duckdb.connect(database=':memory:')
        self.cache = {} # In-memory exact match cache
        
        self.schema_lines = ["Available Tables (DuckDB Dialect):"]
        
        # Register each dataframe as a table in DuckDB
        for name, df in dataframes.items():
            self.con.register(name, df)
            desc = _DF_DESCRIPTIONS.get(name, f"{name} table")
            self.schema_lines.append(f"  • {desc}")
            
            # Add a sample row so the LLM knows exact data types and formats
            if not df.empty:
                sample_row = df.head(1).to_dict(orient="records")[0]
                self.schema_lines.append(f"    Sample Row: {sample_row}")
            
        self.schema_context = "\n".join(self.schema_lines)

    def _generate_sql(self, question: str, history: str = "", error_msg: str = "") -> str:
        prompt = f"""You are an expert SQL Data Analyst.
Given the following database schema:
{self.schema_context}

Write a SQL query (DuckDB dialect) to answer the user's question.
Rules:
- Return ONLY the raw SQL query. Do not include markdown formatting (like ```sql), and do not explain your answer.
- Ensure column names match exactly.

Recent Chat History (for context):
{history}

{f"WARNING: Your previous SQL failed with this error: {error_msg}. Please fix the syntax or column names and try again." if error_msg else ""}

Question: {question}
"""
        response = self.llm.complete(prompt)
        sql = str(response).strip()
        sql = re.sub(r"^```(?:sql)?\n?", "", sql)
        sql = re.sub(r"\n?```$", "", sql)
        return sql.strip()

    def _run_sql(self, sql: str) -> pd.DataFrame:
        """Execute the SQL query and return a Pandas DataFrame."""
        try:
            # DuckDB returns a pandas dataframe easily
            return self.con.execute(sql).df()
        except Exception as e:
            raise ValueError(f"SQL Execution Error: {e}\nQuery was: {sql}")

    def _determine_route(self, question: str, df: pd.DataFrame) -> str:
        """Determines if the output should be TEXT, TABLE, or CHART."""
        if df.empty:
            return "TEXT"
            
        # If it's a single value, it must be text
        if df.shape == (1, 1):
            return "TEXT"
            
        sample = df.head(5).to_string(index=False)
        
        prompt = f"""You are an intelligent data router for a dashboard.
The user asked: "{question}"
We ran a query and got data with shape {df.shape} (rows, cols).
Sample:
{sample}

How should this data be presented? Reply with EXACTLY ONE word:
- CHART: ONLY if the user explicitly asks for a "chart", "graph", "plot", "trend", or "visualize".
- TABLE: ONLY if the user explicitly asked for a "list", "table", "raw data", or "all details". Do NOT return a table for analytical questions.
- TEXT: If the user did not explicitly ask for a table or chart. This is the default for answering any analytical questions like "what factors", "why", "how", or simple facts.

Choice:"""
        response = self.llm.complete(prompt)
        choice = str(response).strip().upper()
        
        if "CHART" in choice: return "CHART"
        if "TABLE" in choice: return "TABLE"
        return "TEXT"

    def _synthesize_text(self, question: str, df: pd.DataFrame, status=None):
        data_str = df.head(20).to_string(index=False)
        
        # Step 1: Drafter Agent
        if status: status.update(label="Drafting initial analysis...", state="running")
        draft_prompt = f"""{SYSTEM_PROMPT}

A data query was run to answer the following question:
"{question}"

The raw output from the query was:
{data_str}

Now write a simple, conversational answer (2-4 sentences) that tells the story behind these numbers.
"""
        draft_response = str(self.llm.complete(draft_prompt)).strip()
        
        # Step 2: Reviewer Agent
        if status: status.update(label="Reviewer is polishing the response...", state="running")
        from app.prompts import REVIEWER_PROMPT
        review_prompt = f"""{REVIEWER_PROMPT}

Original Question: {question}

Draft Answer:
{draft_response}

Please output the final polished version now.
"""
        # Yield streaming chunks from the reviewer
        response_gen = self.llm.stream_complete(review_prompt)
        for chunk in response_gen:
            yield chunk.delta

    def _generate_chart(self, question: str, df: pd.DataFrame) -> go.Figure | str:
        """Generates Plotly Python code to visualize the DataFrame."""
        sample = df.head(5).to_dict(orient="records")
        prompt = f"""You are an expert Data Visualizer using Plotly.
The user asked: "{question}"
We have a pandas DataFrame named `df` with columns: {list(df.columns)}.
Sample data: {sample}

Write Python code using `plotly.graph_objects` as `go` to create a beautiful, modern chart.
Rules:
- Store the final figure in a variable named `fig`.
- Use a dark theme for the layout (e.g., paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white')).
- Do NOT use `fig.show()`.
- Do NOT import pandas or plotly (they are already imported).
- Return ONLY the raw Python code, no markdown, no explanations.
"""
        response = self.llm.complete(prompt)
        code = str(response).strip()
        code = re.sub(r"^```(?:python)?\n?", "", code)
        code = re.sub(r"\n?```$", "", code)
        
        # Execute chart code safely
        local_ns = {"df": df, "go": go, "fig": None}
        try:
            exec(code.strip(), local_ns) # noqa: S102
            fig = local_ns.get("fig")
            if isinstance(fig, go.Figure):
                return fig
            return "⚠️ Failed to generate chart object."
        except Exception as e:
            return f"⚠️ Chart generation failed: {e}"

    def query(self, question: str, history_list: list = None, status=None):
        """Main routing execution with caching, memory, and self-healing."""
        # 1. Check Cache
        if status: status.update(label="Checking memory...", state="running")
        if question in self.cache:
            if status: status.update(label="Serving from cache...", state="complete")
            return self.cache[question]
            
        # 2. Format History
        history_str = ""
        if history_list:
            # Take last 4 messages to avoid blowing up context
            for msg in history_list[-4:]:
                if msg["type"] == "text":
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_str += f"{role}: {msg['content']}\n"
                    
        # 3. Self-Healing SQL Loop
        sql = ""
        df = None
        error_msg = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if status: status.update(label=f"Generating SQL (Attempt {attempt+1})...", state="running")
                sql = self._generate_sql(question, history_str, error_msg)
                if status: status.update(label="Executing query in DuckDB...", state="running")
                df = self._run_sql(sql)
                break # Success!
            except Exception as e:
                error_msg = str(e)
                if attempt == max_retries - 1:
                    if status: status.update(label="Failed to generate correct SQL.", state="error")
                    return f"⚠️ I encountered a data error I couldn't fix: {e}"
        
        # 4. Route Output
        try:
            if status: status.update(label="Routing data...", state="running")
            route = self._determine_route(question, df)
            
            if route == "TABLE":
                self.cache[question] = df
                if status: status.update(label="Complete!", state="complete")
                return df
            elif route == "CHART":
                if status: status.update(label="Generating interactive chart...", state="running")
                result = self._generate_chart(question, df)
                if isinstance(result, str) and result.startswith("⚠️"):
                    # Fallback to streaming text
                    return self._synthesize_text(question, df, status)
                self.cache[question] = result
                if status: status.update(label="Complete!", state="complete")
                return result
            else:
                return self._synthesize_text(question, df, status)
                
        except Exception as e:
            if status: status.update(label="Routing failed.", state="error")
            return f"⚠️ An error occurred during routing: {e}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_chat_engine(dataframes: dict) -> DuckDBEngine | None:
    """Initialises the DuckDB engine."""
    llm = _build_llm()
    if llm is None:
        return None

    valid = {k: v for k, v in dataframes.items() if not v.empty}
    if not valid:
        st.error("No valid datasets loaded. Cannot initialise chat engine.")
        return None

    return DuckDBEngine(dataframes=valid, llm=llm)


def ask_assistant(engine: DuckDBEngine, query: str, history: list = None, status=None):
    """Send a question to the engine with optional history and status."""
    return engine.query(query, history, status)
