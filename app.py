import streamlit as st

from database import initialize_database
from tabs import data_upload_tab, chat_with_ai_tab, data_analysis_tab, CodeExecutionTab


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
    # Use the global database connection
    global conn

    # Initialize session state variables
    initialize_session_state()

    # Streamlit UI - Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Data Upload", "Chat with AI", "Data Analysis", "Code Execution"])

    with tab1:
        data_upload_tab(conn)
    with tab2:
        chat_with_ai_tab(conn)
    with tab3:
        data_analysis_tab(conn)
    with tab4:
        code_execution_tab = CodeExecutionTab(conn)
        code_execution_tab.display()

if __name__ == "__main__":
    main()