import streamlit as st
from anthropic import Anthropic
from groq import Groq
from pandasai.llm.local_llm import LocalLLM
from pandasai import SmartDataframe
from pandasai.llm import  OpenAI  # Import Groq and Anthropic
import pandas as pd
import sqlite3
import uuid
import matplotlib.pyplot as plt
from io import StringIO
import sqlite3
from sqlite3 import Connection
import uuid

# Database Initialization
def initialize_database():
    """Initializes the in-memory SQLite database and creates tables."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Create api_keys table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            service TEXT,
            key TEXT
        )
    ''')

    # Create chat_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id TEXT PRIMARY KEY,
            question TEXT,
            answer TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    return conn

# SQL Utility Functions
def create_view(query: str, conn: Connection) -> pd.DataFrame or str:
    """
    Creates a temporary view from a SQL query.

    Args:
        query (str): SQL query to create the view.
        conn (Connection): SQLite connection object.

    Returns:
        pd.DataFrame or str: Result of the query as a Pandas DataFrame, or an error message.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE VIEW IF NOT EXISTS temp_view AS {query}")
        return pd.read_sql("SELECT * FROM temp_view", conn)
    except Exception as e:
        return str(e)

def execute_sql(query: str, conn: Connection) -> pd.DataFrame or str:
    """
    Executes a SQL query and returns the result.

    Args:
        query (str): SQL query to execute.
        conn (Connection): SQLite connection object.

    Returns:
        pd.DataFrame or str: Result of the query as a Pandas DataFrame, or an error message.
    """
    try:
        return pd.read_sql(query, conn)
    except Exception as e:
        return str(e)

# LLM Initialization Function
def initialize_llm(llm_choice: str, api_key: str = None, cloud_model: str = "OpenAI"):
    """
    Initializes the Language Model based on user choice.

    Args:
        llm_choice (str): User's choice of LLM (Local or Cloud).
        api_key (str, optional): API key for cloud-based LLM. Defaults to None.
        cloud_model (str, optional): The cloud model to use ("OpenAI", "Groq", "Anthropic"). Defaults to "OpenAI".

    Returns:
        LocalLLM or OpenAI or None: Initialized LLM object, or None if initialization fails.
    """
    if llm_choice == "Local":
        return LocalLLM(api_base="http://localhost:11434/v1", model="llama3")  # Hardcoded Llama3
    elif llm_choice == "Cloud":
        if api_key:
            if cloud_model == "OpenAI":
                return OpenAI(api_token=api_key)
            elif cloud_model == "Groq":
                return Groq(api_key=api_key)
            elif cloud_model == "Anthropic":
                return Anthropic(api_key=api_key)
            else:
                st.error("Invalid cloud model selected.")
                return None
        else:
            st.warning("Enter API key for Cloud Mode.")
            return None
    else:
        return None


# Data Loading Functions
def load_excel_data(uploaded_file):
    """
    Loads data from an uploaded Excel file into a Pandas DataFrame.

    Args:
        uploaded_file: The uploaded Excel file.

    Returns:
        pd.DataFrame or None: The loaded DataFrame, or None if loading fails.
    """
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Excel file uploaded successfully!")
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

def load_sqlite_data(sqlite_file):
    """
    Loads data from an uploaded SQLite database and displays table names.

    Args:
        sqlite_file: The uploaded SQLite database file.

    Returns:
        list or None: A list of table names in the database, or None if loading fails.
    """
    try:
        with sqlite3.connect(sqlite_file.name) as conn_db:
            tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn_db)
        table_names = tables['name'].tolist()
        st.success(f"SQLite database loaded. Tables: {', '.join(table_names)}")
        return table_names
    except Exception as e:
        st.error(f"Error loading SQLite database: {e}")
        return None

# Chat Logic Function
def process_chat_prompt(prompt: str, df: pd.DataFrame, llm, conn: Connection):
    """
    Processes the user's chat prompt, executes code, and generates a response.

    Args:
        prompt (str): User's input prompt.
        df (pd.DataFrame): Pandas DataFrame containing the data (if available).
        llm: Initialized Language Model (if available).
        conn (Connection): SQLite connection object for storing chat history.

    Returns:
        str: The generated response to the prompt.
    """
    try:
        # Execute Python Code
        if "```python" in prompt:
            code = prompt.split("```python")[1].split("```")[0]
            exec(code)
            response = "Code executed successfully."

        # Execute SQL Query
        elif "```sql" in prompt:
            query = prompt.split("```sql")[1].split("```")[0]
            result = execute_sql(query, conn)
            response = f"Result:\n{result.to_markdown()}"

        # PandasAI Query
        else:
            if df is not None and llm is not None:
                sdf = SmartDataframe(df, config={"llm": llm})
                response = sdf.chat(prompt)

                # Generate Plots
                if "plot" in prompt.lower():
                    plt.figure()
                    df.plot()
                    st.pyplot(plt)
            else:
                response = "Please upload data and configure the LLM."

    except Exception as e:
        response = f"Error: {str(e)}"

    # Save to Chat History
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (id, question, answer) 
        VALUES (?, ?, ?)
    ''', (str(uuid.uuid4()), prompt, str(response)))

    conn.commit()
    return response


# Streamlit App
def main():
    """Main function to run the Streamlit app."""

    # Initialize database
    conn = initialize_database()

    # Streamlit Session State Initialization
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Streamlit UI
    st.title("AI Data Analyst Chat")

    # File Uploaders
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    sqlite_file = st.file_uploader("Upload SQLite database", type=["db", "sqlite"])

    # Sidebar Settings
    llm_choice = st.sidebar.radio("Choose LLM", ["Local", "Cloud"])

    api_key = None  # Initialize api_key outside conditional scope
    cloud_model = None

    if llm_choice == "Cloud":
        cloud_model = st.sidebar.selectbox("Select Cloud Model", ["OpenAI", "Groq", "Anthropic"])
        api_key = st.sidebar.text_input(f"API Key for {cloud_model}", type="password")

    # Initialize LLM
    llm = initialize_llm(llm_choice, api_key, cloud_model)

    # Load DataFrames
    df = None
    if uploaded_file:
        df = load_excel_data(uploaded_file)

    if sqlite_file:
        load_sqlite_data(sqlite_file)

    # Chat Interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Your question"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Processing..."):
            response = process_chat_prompt(prompt, df, llm, conn)

        with st.chat_message("assistant"):
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Show History
    if st.sidebar.checkbox("Show History"):
        history = pd.read_sql("SELECT question, answer, timestamp FROM chat_history", conn)
        st.sidebar.dataframe(history)

    # Export Data
    if st.sidebar.button("Export History"):
        history = pd.read_sql("SELECT question, answer, timestamp FROM chat_history", conn)
        csv = history.to_csv(index=False)
        st.sidebar.download_button("Download CSV", csv, "chat_history.csv")

if __name__ == "__main__":
    main()