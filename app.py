import sqlite3

import streamlit as st
import multipage_streamlit as mt
import streamlit_nested_layout# NOQA need for work!
from PageData.AiChat import chat_page
from PageData.CodeExecution.code_execution_page import CodeExecutionTab
from PageData.DB.database import initialize_database, DB_PATH
from PageData.DataAnalysis.data_analysis_page import data_analysis_tab
from PageData.Upload.data_upload_page import data_upload_tab
from PageData.Admin.main import admin_panel

# Initialize database connection globally for session persistence
CONN = sqlite3.connect(DB_PATH, uri=True)

def initialize_session_state():
    """Initializes Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "excel_df" not in st.session_state:
        st.session_state["excel_df"] = None
    if "sql_tables" not in st.session_state:
        st.session_state["sql_tables"] = []
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "pandas_gpt_obj" not in st.session_state:
        st.session_state["pandas_gpt_obj"] = None
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = None
    if "selected_python_ids" not in st.session_state:
        st.session_state["selected_python_ids"] = []
    if "selected_sql_tables" not in st.session_state:
        st.session_state["selected_sql_tables"] = []
def data_upload_page():
    data_upload_tab(CONN)

def code_execution_page():
    code_execution_tab = CodeExecutionTab(CONN)
    code_execution_tab.display()

def data_analysis_page():
    data_analysis_tab()

def admin_panel_page():
    admin_panel(CONN)

# Main Streamlit App
def main():
    st.set_page_config(page_title="DDCAI", layout="wide")
    initialize_database(CONN)

    # Initialize session state variables
    initialize_session_state()
    app = mt.MultiPage()
    app.add("Upload 📁", data_upload_page)
    if st.session_state.excel_df is not None:
        app.add("Code Execution 💻", code_execution_page)
        app.add("Data Analysis 📊", data_analysis_page)
        app.add("Admin Panel 🎛️", admin_panel_page)
        app.add("Chat with AI 🤖", chat_page.chat_with_ai_tab)
    app.run_radio()


if __name__ == "__main__":
    main()