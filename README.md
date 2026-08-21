# SwiftKart AI 🛒⚡

An intelligent, instant data analytics dashboard designed for quick-commerce companies. SwiftKart AI acts as your personal Data Analyst—just ask business questions in plain English, and it automatically generates the SQL, queries the data, and returns conversational insights, tables, and visualizations.

## ✨ Features
- **💬 Conversational UI:** A beautiful, WhatsApp-style dark mode chat interface.
- **🧠 Text-to-SQL AI:** Powered by the fast `openai/gpt-oss-20b` (via Groq), capable of writing complex DuckDB SQL queries instantly.
- **🚀 In-Memory Analytics:** Uses DuckDB to query CSV files (`customers.csv` and `orders.csv`) directly in-memory at lightning speed.
- **📊 Interactive Visualizations:** Automatically generates Plotly charts when questions ask for trends or distributions.
- **🇮🇳 Localized for India:** Pre-configured to format all monetary values in Indian Rupees (₹).
- **📥 Data Exports:** 1-click downloads for any generated data table as a CSV.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python, DuckDB
- **AI/LLM:** LlamaIndex, Groq API (gpt-oss-20b model)
- **Data:** Pandas
- **Visualization:** Plotly

## 🚀 How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Tanu019/AI-support-Assistant.git
   cd AI-support-Assistant
   ```

2. **Install dependencies:**
   Make sure you have Python 3.9+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API Key:**
   You will need a Groq API key to power the AI engine.
   - On Windows: `set GROQ_API_KEY=your_api_key_here`
   - On Mac/Linux: `export GROQ_API_KEY=your_api_key_here`

4. **Launch the Dashboard:**
   ```bash
   streamlit run app/main.py
   ```
   The dashboard will open automatically in your browser at `http://localhost:8501`.

## 📂 Project Structure
- `app/main.py`: The main Streamlit application entry point.
- `app/chat_engine.py`: The core LLM and DuckDB engine that handles SQL generation and execution.
- `app/ui_components.py`: Custom CSS and Streamlit UI renderers.
- `app/prompts.py`: System instructions for the AI behavior.
- `data/`: Contains the `customers.csv` and `orders.csv` datasets.
