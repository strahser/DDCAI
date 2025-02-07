from sqlite3 import Connection
import streamlit as st


def delete_api_key(conn: Connection, id: str) -> None:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM api_keys WHERE id = ?", (id,))
    conn.commit()

def update_api_key(conn: Connection, id: str, service: str, key: str) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE api_keys SET service = ?, key = ? WHERE id = ?",
        (service, key, id),
    )
    conn.commit()

def update_code_snippet(conn: Connection, id: str, type_: str, code: str, name: str, is_view: bool, category:str) -> None:
    """Updates a code snippet in the database.  If it's a view, recreates the view."""
    cursor = conn.cursor()
    try:
        if is_view:
            # Get the old view name (assuming it's stored in the 'name' column)
            cursor.execute("SELECT name FROM code_snippets WHERE id = ?", (id,))
            old_view_name = cursor.fetchone()[0]

            # Drop the old view
            cursor.execute(f'DROP VIEW IF EXISTS "{old_view_name}"') # Escape the view name, important for security and compatibility

            # Create the new view
            try:
                cursor.execute(f'CREATE VIEW "{name}" AS {code}')  # Use the new name and code, escape the name
            except Exception as e:
                st.error(f"Error creating view: {e}")
                conn.rollback()  # Rollback the transaction if view creation fails
                return

            # Update the code snippet in the database with the new name and code
            cursor.execute(
                "UPDATE code_snippets SET type = ?, code = ?, name = ?, is_view = ?, category=? WHERE id = ?",
                (type_, code, name, is_view, category, id),
            )
        else:
            # If not a view, just update the snippet
            cursor.execute(
                "UPDATE code_snippets SET type = ?, code = ?, name = ?, is_view = ?, category=? WHERE id = ?",
                (type_, code, name, is_view, category, id),
            )

        conn.commit()
        # st.success(f"Code snippet with ID {id} updated successfully.")

    except Exception as e:
        st.error(f"Error updating code: {e}")
        conn.rollback()  # Rollback the transaction in case of any error

def delete_code_snippet(conn: Connection, code_id: str):
    """Deletes a code snippet from the database. If it's a view, it also drops the view."""
    try:
        cursor = conn.cursor()

        # Check if the code snippet is a view
        cursor.execute("SELECT name, is_view FROM code_snippets WHERE id = ?", (code_id,))
        result = cursor.fetchone()

        if result:
            view_name, is_view = result
            if is_view:
                # Drop the view if it exists
                cursor.execute(f"DROP VIEW IF EXISTS \"{view_name}\"") # Escape the view name

            # Delete the code snippet from the table
            cursor.execute("DELETE FROM code_snippets WHERE id = ?", (code_id,))
            conn.commit()
            st.success(f"Code snippet with ID {code_id} deleted successfully.")
        else:
            st.warning(f"Code snippet with ID {code_id} not found.")

    except Exception as e:
        st.error(f"Error deleting code: {e}")
        conn.rollback()

def create_code_snippet(conn: Connection, type_: str, code: str, name: str, is_view: bool) -> None:
    """Creates a new code snippet in the database. If it's a view, it also creates the view."""
    cursor = conn.cursor()
    try:
        if is_view:
            # Create the view
            try:
                cursor.execute(f"CREATE VIEW \"{name}\" AS {code}")  # Use the new name and code, escape the name
            except Exception as e:
                st.error(f"Error creating view: {e}")
                conn.rollback()  # Rollback the transaction if view creation fails
                return

        # Insert the code snippet into the table
        cursor.execute(
            "INSERT INTO code_snippets (type, code, name, is_view) VALUES (?, ?, ?, ?)",
            (type_, code, name, is_view),
        )
        conn.commit()
        st.success(f"Code snippet '{name}' created successfully.")

    except Exception as e:
        st.error(f"Error creating code snippet: {e}")
        conn.rollback()