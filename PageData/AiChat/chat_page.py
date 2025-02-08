import sqlite3

import streamlit as st
import openai
import pandas_gpt  # NOQA Import the library (it monkey-patches pandas)

from PageData.DB.database import DB_PATH


def initialize_session_state():
    """Initializes session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []


def display_chat_history():
    """Displays the chat history."""
    for role, content in st.session_state["chat_history"]:
        with st.chat_message(role):
            st.markdown(content)


def process_user_input(user_prompt, df):
    """Processes user input using pandas_gpt and updates the chat history."""
    if df is None:
        st.warning("Please upload an Excel file first.")
        return

    if not openai.api_key:
        st.error("Please provide an OpenAI API key.")
        return

    try:
        response = df.ask(user_prompt)  # Use .ask() on the DataFrame
        st.session_state["chat_history"].append(("user", user_prompt))
        st.session_state["chat_history"].append(("assistant", response))

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.session_state["chat_history"].append(("user", user_prompt))
        st.session_state["chat_history"].append(("assistant", f"Error: {e}"))


def chat_with_ai_tab():
    st.title("PandasGPT Chat with DataFrame")

    # 0. Init
    initialize_session_state()

    # 1. API Key Input (Sensitive Information - Do NOT Store Directly in Code)
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    if api_key:
        openai.api_key = api_key
    if api_key and st.button("Save API Key"):
        # Сохраняем ключ в базу данных
        conn = sqlite3.connect(DB_PATH, uri=True)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO api_keys (id, service, key)
            VALUES (?, ?, ?)
        ''', ('openai_user_id', 'OpenAI', api_key))
        conn.commit()  # Предполагается, что переменная connection доступна
        st.success("API Key успешно сохранён!")
    # 2. Load data frame if it exists in session_state
    if "excel_df" in st.session_state and st.session_state["excel_df"] is not None:
        df = st.session_state["excel_df"]
    else:
        df = None #df should default to None in order to display a message
        st.warning("Please upload a DataFrame using the file uploader in the main app.")

    # 3. Display Chat History
    display_chat_history()

    # 4. Chat Input and Response
    if df is not None and (prompt := st.chat_input("Ask questions about your DataFrame:")):#Skip unless a df is loaded
        process_user_input(prompt, df)
        st.rerun()