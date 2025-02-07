
import pandas as pd
import streamlit as st
from PageData.CodeExecution.PythonCodeHandler import PythonCodeHandler
from PageData.CodeExecution.SqlCodeHandler import SqlCodeHandler
from PageData.DB.database import execute_sql


class CodeExecutionTab:
    """Main class for managing code execution tabs."""

    def __init__(self, conn):
        """
        Initializes the CodeExecutionTab.

        Args:
            conn: The database connection object.
        """
        self.conn = conn
        self.sql_handler = SqlCodeHandler(conn)
        self.python_handler = PythonCodeHandler(conn)
        self.output_placeholder = None

    def display(self):
        """Displays all UI components, including tabs for SQL and Python code execution."""
        st.header("Code Execution")
        self.output_placeholder = st.empty()

        # Set the common output placeholder for both handlers
        self.sql_handler.set_output_placeholder(self.output_placeholder)
        self.python_handler.set_output_placeholder(self.output_placeholder)

        sql_tab, python_tab = st.tabs(["SQL", "Python"])
        with sql_tab:
            self.sql_handler.display_form()
        with python_tab:
            self.python_handler.display_form()

        self.display_saved_scripts()

    def display_saved_scripts(self):
        """Displays saved scripts and available views."""
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Saved Scripts")
            scripts = execute_sql("SELECT id, name, type, is_view, category FROM code_snippets", self.conn)
            if isinstance(scripts, pd.DataFrame) and not scripts.empty:
                st.dataframe(scripts)
            else:
                st.info("No saved scripts available.")

        with col2:
            st.subheader("Available Views")
            views_df = execute_sql("SELECT name FROM code_snippets WHERE is_view = 1", self.conn)
            if isinstance(views_df, pd.DataFrame) and not views_df.empty:
                views = views_df['name'].tolist()
                st.write(views)
            else:
                st.info("No views available.")