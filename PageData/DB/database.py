import io
import os
import sqlite3
from sqlite3 import Connection
import pandas as pd
import streamlit as st
import uuid
import tempfile
DB_PATH = "file::memory:?cache=shared"

def save_database(conn):
    """
    Saves the in-memory SQLite database to a byte stream using a temporary file.

    Args:
        conn: The SQLite connection object to the in-memory database.

    Returns:
        bytes: The database as a byte stream, or None if an error occurred.
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            temp_filename = tmp_file.name

        # Connect to the temporary file as a database
        temp_conn = sqlite3.connect(temp_filename)

        # Backup the in-memory database to the temporary file
        with temp_conn:
            conn.backup(temp_conn)

        temp_conn.close() # Close temporary connection to get the data flushed to disk

        # Read the temporary file into a byte stream
        with open(temp_filename, "rb") as f:
            db_bytes = f.read()

        # Remove the temporary file
        os.remove(temp_filename)

        return db_bytes

    except Exception as e:
        st.error(f"Error creating database byte stream: {e}")
        return None

def initialize_database() -> Connection:
    """Initializes the in-memory SQLite database and creates tables."""
    conn = sqlite3.connect(DB_PATH, uri=True)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            service TEXT,
            key TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id TEXT PRIMARY KEY,
            question TEXT,
            answer TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_snippets (
            id TEXT PRIMARY KEY,
            type TEXT,
            code TEXT,
            name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_view BOOLEAN DEFAULT FALSE,
            category TEXT  -- Added the category field
        )
    ''')

    conn.commit()
    return conn

def create_view(query: str, conn: Connection, view_name: str = "temp_view") -> pd.DataFrame or str:
    """Creates a temporary view from a SQL query."""
    try:
        cursor = conn.cursor()
        _query = f"CREATE VIEW IF NOT EXISTS \"{view_name}\" AS {query}"
        cursor.execute(_query)
        conn.commit()
        return pd.read_sql(f"SELECT * FROM \"{view_name}\"", conn)
    except Exception as e:
        return str(e)

def execute_sql(query: str, conn: Connection) -> pd.DataFrame or str:
    """Executes a SQL query and returns the result."""
    try:
        return pd.read_sql(query, conn)
    except Exception as e:
        return str(e)

def get_only_views_names(conn: Connection) -> list:
    """Retrieves table and view names from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE  type='view';")
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    except Exception as e:
        st.error(f"Error retrieving view names: {e}")
        return []

def get_table_names(conn: Connection) -> list:
    """Retrieves table and view names from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' OR type='view';")
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    except Exception as e:
        st.error(f"Error retrieving table names: {e}")
        return []


def update_record(conn: sqlite3.Connection, table_name: str, record_id: str, dict): #data is now a param
    """Updates a record in the specified table."""
    try:
        cursor = conn.cursor()
        placeholders = ", ".join(f"\"{key}\" = ?" for key in dict)
        update_sql = f"UPDATE \"{table_name}\" SET {placeholders} WHERE id = ?"
        values = list(dict.values()) + [record_id]

        cursor.execute(update_sql, values)
        conn.commit()
        st.success(f"Record with ID {record_id} in table {table_name} updated successfully.")
    except Exception as e:
        st.error(f"Error updating record: {e}")
        conn.rollback()

def insert_code_snippet(conn: Connection, code_type: str, code: str, name: str, is_view: bool = False, category: str = None):
    """Inserts a code snippet into the database."""

    code_id = str(uuid.uuid4())
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO code_snippets (id, type, code, name, is_view, category) VALUES (?, ?, ?, ?, ?, ?)",
                       (code_id, code_type, code, name, is_view, category))
        conn.commit()
        st.success(f"{code_type.upper()} code saved successfully with ID: {code_id}")
    except Exception as e:
        st.error(f"Error saving {code_type} code: {e}")

def execute_sql_text(query: str, conn: Connection) -> str or None:
    """Executes a SQL query and returns a single text result."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result[0]  # Return the first column from the first row
        else:
            return None  # Return None if no result is found
    except Exception as e:
        return str(e)

def delete_view_by_name(conn: Connection, view_name: str):
    """Deletes a view from the database."""
    try:
        cursor = conn.cursor()
        # Drop the view
        cursor.execute(f"DROP VIEW IF EXISTS \"{view_name}\"")  # Escape the view name
        # Delete the code snippet from the table
        cursor.execute("DELETE FROM code_snippets WHERE name = ? AND is_view = 1", (view_name,))
        conn.commit()
        st.success(f"View '{view_name}' deleted successfully.")

    except Exception as e:
        st.error(f"Error deleting view: {e}")
        conn.rollback()

