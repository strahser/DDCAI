import streamlit as st

from PageData.Admin.AdminTab import AdminTab
from PageData.Admin.Utils.DbUtils import delete_code_snippet, update_code_snippet
from PageData.DB.database import execute_sql


class CodeSnippetsTab(AdminTab):
    """Tab for managing code snippets."""

    def __init__(self, conn):
        """
        Initializes the CodeSnippetsTab.

        Args:
            conn: Database connection object.
        """
        super().__init__(conn, "Code Snippets Management")

    def load_data(self):
        """Loads code snippet data from the database."""
        self.data = execute_sql("SELECT * FROM code_snippets", self.conn)

    def get_column_config(self):
        """Returns the column configuration for the code snippets editor."""
        if self.data is not None and 'category' in self.data:
            categories = self.data["category"].unique()
        else:
            categories = []  # Or a default list of categories if none are available

        return {
            "id": st.column_config.TextColumn(disabled=True),
            "type": st.column_config.SelectboxColumn(
                options=["python", "sql"],
                required=True
            ),
            "code": st.column_config.TextColumn(),
            "name": st.column_config.TextColumn(),
            "category": st.column_config.TextColumn(),
            "is_view": st.column_config.CheckboxColumn(required=True),
            "delete": st.column_config.CheckboxColumn()
        }

    def delete_entry(self, row):
        """Deletes a code snippet from the database."""
        delete_code_snippet(self.conn, row["id"])

    def update_entry(self, row):
        """Updates a code snippet in the database."""
        update_code_snippet(
            self.conn,
            row["id"],
            row["type"],
            row["code"],
            row["name"],
            row["is_view"],
            row["category"]
        )
