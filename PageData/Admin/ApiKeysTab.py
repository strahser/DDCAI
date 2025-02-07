import streamlit as st

from PageData.Admin.AdminTab import AdminTab
from PageData.Admin.Utils.DbUtils import delete_api_key, update_api_key
from PageData.DB.database import execute_sql


class ApiKeysTab(AdminTab):
    """Tab for managing API keys."""

    def __init__(self, conn):
        """
        Initializes the ApiKeysTab.

        Args:
            conn: Database connection object.
        """
        super().__init__(conn, "API Keys Management")

    def load_data(self):
        """Loads API key data from the database."""
        self.data = execute_sql("SELECT * FROM api_keys", self.conn)

    def get_column_config(self):
        """Returns the column configuration for the API keys editor."""
        return {
            "id": st.column_config.TextColumn(disabled=True),
            "service": st.column_config.TextColumn(),
            "key": st.column_config.TextColumn(),
            "delete": st.column_config.CheckboxColumn(required=True)
        }

    def delete_entry(self, row):
        """Deletes an API key from the database."""
        delete_api_key(self.conn, row["id"])

    def update_entry(self, row):
        """Updates an API key in the database."""
        update_api_key(self.conn, row["id"], row["service"], row["key"])