import os
import sqlite3
import pandas as pd
import streamlit as st
from PageData.Upload.sql_from_df_creator import   create_sql_table
from PageData.DB.database import get_table_names, save_database, execute_sql
from PageData.Upload.upload_ddc import upload_ddc, visualise_loads


def save_database_button(conn):
    """Handles database download functionality using st.download_button.

    Args:
        conn: The SQLite connection object to the in-memory database.
    """
    db_bytes = save_database(conn)
    if db_bytes:
        st.sidebar.download_button(
            label="Download Database",
            data=db_bytes,
            file_name="chat_data.db",
            mime="application/vnd.sqlite3",
        )

def handle_sqlite_upload(uploaded_file,conn):
    """
    Handles the uploaded SQLite file, overwriting or creating the in-memory database.

    Args:
        uploaded_file: The uploaded file from st.file_uploader.
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
                with open(db_file, "wb") as f: #Write to temporary db file. This gets rid of the decoding error, and works as expected
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
            st.error(f"Failed to upload file. The file might not be a valid SQLite database or it might be corrupted. Error: {e}")
    else:
        st.info("Please upload a database file.")

def data_upload_tab(conn):
    """Handles the Data Upload tab."""
    col1, col2 = st.columns(2)
    df = st.session_state["excel_df"]
    excel_handle_condition = "excel_df" in  st.session_state and isinstance(df, pd.DataFrame)
    with col1:
        upload_ddc()#genereted df in session from ddc excel file or ddc revit file

    with col2:
        st.subheader("Data Preview and SQL Tables")
        sqlite_file = st.file_uploader("Upload SQLite database", type=["db", "sqlite"])
        if sqlite_file:
            handle_sqlite_upload(sqlite_file, conn)
        if st.sidebar.button("Save Database"):
            save_database_button(conn)
        if excel_handle_condition:
            if st.button("Create SQL table from Excel data"):
                create_sql_table(df, conn)
                st.session_state["sql_tables"] = get_table_names(conn)
        sql_table = get_table_names(conn)
        if "_df" in sql_table:
            _query = "select * from _df"
            res = execute_sql(_query, conn)
            if st.button("Update session from sql data") and isinstance(res, pd.DataFrame):
                st.session_state["excel_df"] = res
                st.info("update data in session from sql table")
        st.write("SQL Tables:")
        st.write(sql_table)  # Display SQL tables
    with st.expander("## Preview"):
        visualise_loads()


