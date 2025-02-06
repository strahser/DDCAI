import streamlit as st

from PageData.AiChat import chat_page
from PageData.CodeExecution.code_execution_page import CodeExecutionTab
from PageData.DB.database import initialize_database
import multipage_streamlit as mt

from PageData.DataAnalysis.data_analysis_page import data_analysis_tab
from PageData.Upload.data_upload_page import data_upload_tab
from PageData.admin import admin_panel

# Initialize database connection globally for session persistence
conn = initialize_database()

def initialize_session_state():
    """Initializes Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "excel_df" not in st.session_state:
        st.session_state["excel_df"] = None
    if "sql_tables" not in st.session_state:
        st.session_state["sql_tables"] = []


# Main Streamlit App
def main():
    st.set_page_config(page_title="DDCAI", layout="wide")
    # Use the global database connection
    global conn
    def data_upload_page():
        data_upload_tab(conn)

    def code_execution_page():
        code_execution_tab = CodeExecutionTab(conn)
        code_execution_tab.display()

    def data_analysis_page():
        data_analysis_tab(conn)

    def admin_panel_page():
        admin_panel(conn)

    # Initialize session state variables
    initialize_session_state()
    app = mt.MultiPage()
    app.add("Upload 📁", data_upload_page)
    if st.session_state.excel_df is not None:
        app.add("Chat with AI 🤖", chat_page.chat_with_ai_tab)
        app.add("Code Execution 💻", code_execution_page)
        app.add("Data Analysis 📊", data_analysis_page)
        app.add("Admin Panel 🎛️", admin_panel_page)
    app.run_radio()


if __name__ == "__main__":
    main()