import sqlite3

import streamlit as st
from io import StringIO
import pandas as pd
import sys
from PageData.DB.database import create_view, execute_sql, insert_code_snippet, get_table_names, DB_PATH
from PageData.utils import get_common_vars, execute_python_code
from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES

class CodeExecutionTab:
    def __init__(self, conn):
        self.conn = conn
        self.reset_state()
        self.output_placeholder = None  # Single shared placeholder
        self.category = "Default" #Added default empty category

    def reset_state(self):
        """Resets all internal states to default."""
        self.sql_code = "SELECT * FROM _df LIMIT 10;"
        self.python_code = (
            "df = st.session_state.get('excel_df')\n"
            "if df is not None:\n"
            "    st.write(df.head())\n"
            "else:\n"
            "    st.write('No dataframe loaded. Please upload data.')"
        )
        self.sql_code_name = "Untitled SQL Script"
        self.python_code_name = "Untitled Python Script"
        self.view_name = "Untitled View"
        self.category = "" # Added category value

    def _handle_sql_execute(self):
        if self.sql_code:
            conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
            try:
                result = execute_sql(self.sql_code, conn)
                if isinstance(result, pd.DataFrame):
                    self.output_placeholder.dataframe(result)  # Use the shared placeholder
                else:
                    self.output_placeholder.error(result)
            except Exception as e:
                self.output_placeholder.error(f"SQL execution error: {e}")
            conn.close()

    def _handle_sql_save(self):
        if self.sql_code and self.sql_code_name:
            conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
            insert_code_snippet(conn, "sql", self.sql_code, self.sql_code_name, category = self.category)
            self.output_placeholder.success("SQL script saved!") #Placeholder
            conn.close()

    def _handle_sql_create(self):
        if self.sql_code and self.view_name:
            conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
            result = create_view(self.sql_code, conn, self.view_name)
            if isinstance(result, str):
                self.output_placeholder.error(f"View creation failed: {result}")
            else:
                insert_code_snippet(conn, "sql", self.sql_code, self.view_name, is_view=True, category = self.category)
                self.output_placeholder.success("View created successfully!")
            conn.close()

    def _handle_python_execute(self):
        if self.python_code:
            output, error = execute_python_code(self.python_code, get_common_vars())
            if error:
                self.output_placeholder.error(f"Execution error: { error}") #Placeholder
            else:
                self.output_placeholder.text(output or "No output generated")

    def _handle_python_save(self):
        if self.python_code and self.python_code_name:
            conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
            insert_code_snippet(conn, "python", self.python_code, self.python_code_name, category = self.category)
            self.output_placeholder.success("Python script saved!")#Placeholder
            conn.close()

    def display(self):
        """Displays the Code Execution tab using tabs for SQL and Python forms."""
        st.header("Code Execution")

        sql_tab, python_tab = st.tabs(["SQL", "Python"])

        # Create the output placeholder BEFORE the forms
        self.output_placeholder = st.empty()

        with sql_tab:
            self.display_sql_form()
        with python_tab:
            self.display_python_form()

        self.display_saved_scripts() #Add to display the data

    def display_sql_form(self):
        """Displays the SQL Code form with execute, save, and create view options."""
        self.sql_code = st_ace(
            value=self.sql_code,
            placeholder="Type Query",
            language="sql",
            theme=THEMES.index("xcode"),
            key="sql_code"
        )
        self.sql_code_name = st.text_input("Script Name:", value=self.sql_code_name)
        self.view_name = st.text_input("View Name:", value=self.view_name)
        self.category = st.text_input("Category", value=self.category, key="sql_category") # Adds a category to the SQL FORM. Added key
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Execute SQL", key="sql_execute"):
                self._handle_sql_execute()
        with col2:
            if st.button("Save SQL Script", key="sql_save"):
                self._handle_sql_save()
        with col3:
            if st.button("Save SQL View", key="sql_view_create"):
                self._handle_sql_create()

    def display_python_form(self):
        """Displays the Python Code form with execute and save options."""
        self.python_code  = st_ace(
            value=self.python_code,
            placeholder="Type Query",
            language="python",
            theme=THEMES.index("xcode"),
            key="python_code"
        )

        self.python_code_name = st.text_input("Script Name:", value=self.python_code_name)
        self.category = st.text_input("Category", value=self.category, key="python_category") # Adds a category to the Python FORM. Added key

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Execute Python", key="python_execute"):
                self._handle_python_execute()
        with col2:
            if st.button("Save Python", key="python_save"):
                self._handle_python_save()

    def display_saved_scripts(self):
        """Displays saved scripts and available views."""
        conn = self.conn
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Saved Scripts")
            scripts = execute_sql("SELECT id, name, type, is_view, category FROM code_snippets", conn)
            if isinstance(scripts, pd.DataFrame) and not scripts.empty: #Added security
                st.dataframe(scripts)
            else:
                st.info("No saved scripts available.")

        with col2:
            st.subheader("Available Views")
            tables = get_table_names(conn)
            if tables:
                # Fetch view names from code_snippets table where is_view is True
                views_df = execute_sql("SELECT name FROM code_snippets WHERE is_view = 1", conn)
                if isinstance(views_df, pd.DataFrame) and not views_df.empty:
                    views = views_df['name'].tolist()  # Extract list of view names
                    st.write(list(views))
                else:
                    st.info("No views available.")
            else:
                st.info("No tables found in the database.")