import streamlit as st
from streamlit_ace import st_ace, THEMES

from PageData.CodeExecution.BaseCodeHandler import BaseCodeHandler
from PageData.DB.database import insert_code_snippet
from PageData.utils import execute_python_code, get_common_vars


class PythonCodeHandler(BaseCodeHandler):
    """Handler for Python code."""

    def __init__(self, conn):
        """
        Initializes the PythonCodeHandler.

        Args:
            conn: The database connection object.
        """
        super().__init__(conn)
        self.reset_state()

    def reset_state(self):
        """Resets the state to default values, including initial Python code."""
        super().reset_state()
        self.code = (
            "df = st.session_state.get('excel_df')\n"
            "if df is not None:\n"
            "    st.write(df.head())\n"
            "else:\n"
            "    st.write('No dataframe loaded. Please upload data.')"
        )
        self.code_name = "Untitled Python Script"

    def display_form(self):
        """Displays a form for entering Python code, script name, and category."""
        self.code = st_ace(
            value=self.code,
            placeholder="Type Python Code",
            language="python",
            theme=THEMES.index("xcode"),
            key="python_code"
        )
        self.code_name = st.text_input("Script Name:", value=self.code_name, key="python_name")
        self.category = st.text_input("Category", value=self.category, key="python_category")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Execute Python", key="python_execute"):
                self.handle_execute()
        with col2:
            if st.button("Save Python", key="python_save"):
                self.handle_save()

    def handle_execute(self):
        """Executes the Python code and displays the output or error."""
        if self.code:
            output, error = execute_python_code(self.code, get_common_vars())
            if error:
                self.output_placeholder.error(f"Execution error: {error}")
            else:
                self.output_placeholder.text(output or "No output generated")

    def handle_save(self):
        """Saves the Python script to the database."""
        if self.code and self.code_name:
            insert_code_snippet(self.conn, "python", self.code, self.code_name,
                                category=self.category)
            self.output_placeholder.success("Python script saved!")