import pandas as pd

from PageData.DB.database import execute_sql, get_only_views_names, delete_view_by_name

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
        st.success(f"Code snippet with ID {id} updated successfully.")

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



def admin_panel(conn):
    """Displays the admin panel for managing data."""
    st.title("Admin Panel")
    tab1, tab2, tab3 = st.tabs(["Code Snippets", "Views", "API Keys"])

    with tab1:
        st.header("Code Snippets Management")

        # Display and manage Code Snippets
        code_snippets = execute_sql("SELECT * FROM code_snippets", conn)
        if code_snippets is not None and not code_snippets.empty:
            code_snippets['delete'] = False  # Add a checkbox column for deletion

            # Configure columns for data editor
            col_config = {
                "id": st.column_config.TextColumn(disabled=True),
                "type": st.column_config.SelectboxColumn(options=["python", "sql"], required=True),
                "code": st.column_config.TextColumn(),
                "name": st.column_config.TextColumn(),
                "is_view": st.column_config.CheckboxColumn(required=True),
                "delete": st.column_config.CheckboxColumn()
            }

            edited_snippets = st.data_editor(
                code_snippets,
                column_config=col_config,
                key="code_snippets_editor",
                hide_index=True #Hide the index.
            )

            # Handle Updates and Deletions
            if st.button("Apply Changes"):
                for index, row in edited_snippets.iterrows():
                    if row["delete"]:
                        delete_code_snippet(conn, row["id"])
                    else:
                        update_code_snippet(conn, row["id"], row["type"], row["code"], row["name"], row["is_view"],row["category"])
                st.success("Changes Applied")
        else:
            st.info("No code snippets found.")

    with tab2:
        st.header("View Management")

        # View Creation Form
        with st.form("create_view_form"):
            view_name = st.text_input("View Name", help="The name of the view to be created.")
            view_code = st.text_area("View Code", help="The SQL code for the view definition.")
            create_button = st.form_submit_button("Create View")

            if create_button:
                create_code_snippet(conn, type_="sql", code=view_code, name=view_name, is_view=True)

        # Display existing views
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        existing_views = [row[0] for row in cursor.fetchall()]  # Extract view names
        # Display existing views

        if existing_views:
            st.subheader("Existing Views")
            # Create a DataFrame for display and deletion
            view_data = pd.DataFrame({"View Name": existing_views, "Delete": [False] * len(existing_views)})
            col_config = {
                "View Name": st.column_config.TextColumn(disabled=True),
                "Delete": st.column_config.CheckboxColumn()
            }
            edited_views = st.data_editor(view_data, column_config=col_config, key="view_editor", hide_index=True)

            if st.button("Apply View Changes"):
                for index, row in edited_views.iterrows():
                    if row["Delete"]:
                        delete_view_by_name(conn, row["View Name"])
                st.success("View changes applied!")

        else:
            st.info("No views found.")

    with tab3:
        st.header("API Keys Management")

        # Display and manage API Keys
        api_keys = execute_sql("SELECT * FROM api_keys", conn)
        if api_keys is not None and not api_keys.empty:
            # Add a checkbox column for deletion
            api_keys['delete'] = False

            # Use data_editor for in-place editing and deletion selection
            col_config = {
                "id": st.column_config.TextColumn(disabled=True),  # Disable editing of the ID
                "service": st.column_config.TextColumn(),
                "key": st.column_config.TextColumn(),
                "delete": st.column_config.CheckboxColumn(required=True) #For deleting
            }

            edited_api_keys = st.data_editor(
                api_keys,
                column_config=col_config,
                key="api_keys_editor",
                hide_index=True #Hide index.
            )

            # Handle Updates, Delete
            if st.button("Apply Changes"): #The button should be the last thing that happens.
                for index, row in edited_api_keys.iterrows():
                    if row["delete"]:
                        delete_api_key(conn, row["id"])
                    else:
                        update_api_key(conn, row["id"], row["service"], row["key"])
                st.success("Changes Applied")
        else:
            st.info("No API keys found.")




