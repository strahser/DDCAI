import os
import sqlite3
from sqlite3 import Connection

import pandas as pd
import streamlit as st
from PageData.Upload.sql_from_df_creator import create_sql_table
from PageData.DB.database import get_table_names, save_database, execute_sql, get_tables_and_views_info
from PageData.Upload.upload_ddc import upload_ddc, visualise_loads


def save_database_button(conn):
    """Handles database download functionality using st.download_button.

    Args:
        conn: The SQLite connection object to the in-memory database.
    """
    db_bytes = save_database(conn)
    if db_bytes:
        st.sidebar.download_button(
            label="📥 Download Database",
            data=db_bytes,
            file_name="chat_data.db",
            mime="application/vnd.sqlite3",
        )


def handle_sqlite_upload(uploaded_file, conn):
    """
    Handles the uploaded SQLite file, overwriting or creating the in-memory database.

    Args:
        uploaded_file: The uploaded file from st.file_uploader.
        :param uploaded_file:
        :param conn:
    """

    if uploaded_file is not None:
        try:
            # Read the uploaded file content as bytes
            file_content = uploaded_file.read()

            # Load the database from the uploaded file into the in-memory database
            with conn:
                # Use executemany to insert bytes directly.  No decoding is needed for binary data.
                # We'll need to know the schema to re-create tables if the database is meant to be used this way.

                # Option 1: Load into a new DB.  This assumes your file is a complete DB, and uses backup.
                db_file = uploaded_file.name  # Get the filename for temporary storage
                with open(db_file,
                          "wb") as f:  # Write to temporary db file. This gets rid of the decoding error, and works
                    # as expected
                    f.write(file_content)

                # Create a temporary connection to the uploaded file. This requires a file, not bytes.
                temp_conn = sqlite3.connect(db_file)

                # Backup the uploaded data to the in memory db
                conn.backup(temp_conn)  # Backup to in-memory database

                temp_conn.close()
                os.remove(db_file)

            st.success("Database uploaded successfully.")

        except sqlite3.Error as e:
            st.error(f"Error uploading database: {e}")
        except Exception as e:
            st.error(
                f"Failed to upload file. The file might not be a valid SQLite database or it might be corrupted. Error: {e}")
    else:
        st.info("Please upload a database file.")


def data_upload_tab(conn: Connection):
    """Handles the Data Upload tab."""
    # Check if excel_df exists and is a DataFrame
    excel_handle_condition = "excel_df" in st.session_state and isinstance(st.session_state["excel_df"], pd.DataFrame)

    with st.sidebar:  # Group sidebar elements
        if st.button("💾  Save Database to file"):
            save_database_button(conn)
        excel_to_sql_button = st.button("SQL from session 📊➡️🗄️")
        sql_to_session_button=st.button("Session from SQL 🗄️➡️💻")

    with st.expander("Load Data"):  # Nested expander
        upload_ddc()  # generate df in session from ddc excel file or ddc revit file

        st.subheader("SQL Data Upload")
        sqlite_file = st.file_uploader("Upload SQLite database", type=["db", "sqlite"], help="Load config SQL file")
        if sqlite_file:
            handle_sqlite_upload(sqlite_file, conn)

        if excel_to_sql_button and excel_handle_condition:
            create_sql_table(st.session_state["excel_df"], conn)
            st.session_state["sql_tables"] = get_table_names(conn)

        sql_table = get_tables_and_views_info(conn)

        if "_df" in sql_table["Name"].values: # Check if table exists using its name
            _query = "SELECT * FROM _df"
            res = execute_sql(_query, conn)
            if sql_to_session_button and isinstance(res, pd.DataFrame):
                st.session_state["excel_df"] = res
                st.success("updated data in session from sql table")

    with st.expander("Preview"):
        st.subheader("SQL Tables Preview:")
        st.write(sql_table)  # Display SQL tables
        visualise_loads()

