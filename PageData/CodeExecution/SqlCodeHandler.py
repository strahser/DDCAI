import sqlite3
import pandas as pd
import streamlit as st
from streamlit_ace import st_ace, THEMES

from PageData.CodeExecution.BaseCodeHandler import BaseCodeHandler
from PageData.DB.database import create_view, execute_sql, insert_code_snippet, get_table_names
from PageData.utils import execute_python_code, get_common_vars


class SqlCodeHandler(BaseCodeHandler):
    """Handler for SQL code."""

    def __init__(self, conn):
        """
        Initializes the SqlCodeHandler.

        Args:
            conn: The database connection object.
        """
        super().__init__(conn)
        self.reset_state()

    def reset_state(self):
        """Resets the state to default values including initial SQL code and names."""
        super().reset_state()
        self.code = "SELECT * FROM _df LIMIT 10;"
        self.code_name = "Untitled SQL Script"
        self.view_name = "Untitled View"

    def display_form(self):
        """Displays a form for entering SQL code, script name, view name, and category."""
        self.code = st_ace(
            value=self.code,
            placeholder="Type SQL Query",
            language="sql",
            theme=THEMES.index("xcode"),
            key="sql_code"
        )
        self.code_name = st.text_input("Script Name:", value=self.code_name, key="sql_name")
        self.view_name = st.text_input("View Name:", value=self.view_name, key="sql_view_name")
        self.category = st.text_input("Category", value=self.category, key="sql_category")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Execute SQL", key="sql_execute"):
                self.handle_execute()
        with col2:
            if st.button("Save SQL Script", key="sql_save"):
                self.handle_save()
        with col3:
            if st.button("Save SQL View", key="sql_view_create"):
                self.handle_create_view()

    def handle_execute(self):
        """Executes the SQL code and displays the result."""
        if self.code:
            try:
                result = execute_sql(self.code, self.conn)
                if isinstance(result, pd.DataFrame):
                    self.output_placeholder.dataframe(result)
                else:
                    self.output_placeholder.error(result)
            except Exception as e:
                self.output_placeholder.error(f"SQL execution error: {e}")

    def handle_save(self):
        """Saves the SQL script to the database."""
        if self.code and self.code_name:
            insert_code_snippet(self.conn, "sql", self.code, self.code_name,
                                category=self.category)
            self.output_placeholder.success("SQL script saved!")

    def handle_create_view(self):
        """Creates a SQL view in the database."""
        if self.code and self.view_name:
            result = create_view(self.code, self.conn, self.view_name)
            if isinstance(result, str):
                self.output_placeholder.error(f"View creation failed: {result}")
            else:
                insert_code_snippet(self.conn, "sql", self.code, self.view_name,
                                    is_view=True, category=self.category)
                self.output_placeholder.success("View created successfully!")