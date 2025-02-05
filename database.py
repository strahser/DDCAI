import sqlite3
from sqlite3 import Connection
import pandas as pd
import streamlit as st
import io

def initialize_database() -> Connection:
    """Initializes the in-memory SQLite database and creates tables."""
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
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
            is_view BOOLEAN DEFAULT FALSE
        )
    ''')

    conn.commit()
    return conn

def create_view(query: str, conn: Connection, view_name: str = "temp_view") -> pd.DataFrame or str:
    """Creates a temporary view from a SQL query."""
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE VIEW IF NOT EXISTS \"{view_name}\" AS {query}")
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

def save_database(conn: Connection, filename: str = "chat_data.db"):
    """Saves the in-memory database to a file."""
    try:
        buffer = io.BytesIO()
        with sqlite3.connect(':memory:') as backup_conn:
            cursor = backup_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM main.{table_name};")
                backup_conn.commit()
            conn.backup(backup_conn)
        buffer.seek(0)
        db_bytes = buffer.read()
        return db_bytes
    except Exception as e:
        st.error(f"Error saving database: {e}")
        return None

def insert_code_snippet(conn: Connection, code_type: str, code: str, name: str, is_view: bool = False):
    """Inserts a code snippet into the database."""
    import uuid # this is only needed in this function, so you only want this to be imported as this function is called
    code_id = str(uuid.uuid4())
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO code_snippets (id, type, code, name, is_view) VALUES (?, ?, ?, ?, ?)",
                       (code_id, code_type, code, name, is_view))
        conn.commit()
        st.success(f"{code_type.upper()} code saved successfully with ID: {code_id}")
    except Exception as e:
        st.error(f"Error saving {code_type} code: {e}")

def delete_code_snippet(conn: Connection, code_id: str):
    """Deletes a code snippet from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM code_snippets WHERE id = ?", (code_id,))
        conn.commit()
        st.success(f"Code snippet with ID {code_id} deleted successfully.")
    except Exception as e:
        st.error(f"Error deleting code: {e}")

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