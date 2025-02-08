import sqlite3

import streamlit as st
import multipage_streamlit as mt
import streamlit_nested_layout  # NOQA need for work!

from PageData.AiChat.chat_page import chat_with_ai_tab
from PageData.CodeExecution.code_execution_page import CodeExecutionTab
from PageData.DB.database import initialize_database, DB_PATH
from PageData.DataAnalysis.DataAnalysisApp import DataAnalysisApp
from PageData.Upload.data_upload_page import data_upload_tab
from PageData.Admin.main import admin_panel


class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path=DB_PATH, uri=True):
        if not self._initialized:
            self.conn = sqlite3.connect(db_path, uri=uri)
            self._initialized = True

    def get_connection(self):
        return self.conn

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self._instance = None


# Initialize database connection globally for session persistence
db = DatabaseConnection()
# CONN = sqlite3.connect(DB_PATH, uri=True)
CONN = db.get_connection()


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
    if 'global_python_select' not in st.session_state:
        st.session_state.global_python_select = []
    if 'global_sql_select' not in st.session_state:
        st.session_state.global_sql_select = []


def data_upload_page():
    data_upload_tab(CONN)


def code_execution_page_run():
    code_execution_tab = CodeExecutionTab(CONN)
    code_execution_tab.display()


def data_analysis_page_run():
    data_analise = DataAnalysisApp(CONN)
    data_analise.data_analysis_tab_run()


def admin_panel_page_run():
    admin_panel(CONN)


def chat_page_run():
    chat_with_ai_tab()


# Main Streamlit App
def main():
    st.set_page_config(page_title="DDCAI", layout="wide")
    initialize_database(CONN)

    # Initialize session state variables
    initialize_session_state()
    app = mt.MultiPage()
    app.add("Upload 📁", data_upload_page)
    if st.session_state.excel_df is not None:
        app.add("Code Execution 💻", code_execution_page_run)
        app.add("Data Analysis 📊", data_analysis_page_run)
        app.add("Admin Panel 🎛️", admin_panel_page_run)
        app.add("Chat with AI 🤖", chat_page_run)
    app.run_radio()


if __name__ == "__main__":
    main()
