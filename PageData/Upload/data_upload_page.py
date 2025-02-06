import streamlit as st
from PageData.Upload.data_loader import load_excel_data, load_sqlite_data, create_sql_table
from PageData.DB.database import  get_table_names
from PageData.DB.database import save_database
def handle_excel_upload(file, conn, create_table: bool,col1,col2):
    """Processes Excel file upload."""

    with col1:
        st.subheader("Upload Settings")
        if file:  # Only proceed if a file has been uploaded
            st.session_state.uploaded_file_name = file.name
            df = load_excel_data(file, conn)
            if df is not None:
                st.session_state["excel_df"] = df

                if create_table:
                    if 'excel_df' in st.session_state:  # Check if 'excel_df' exists in session_state
                        df = st.session_state["excel_df"]
                        if create_sql_table(df, conn):
                            st.session_state["sql_tables"] = get_table_names(conn)
                        else:
                            st.error("Failed to create SQL table.")
                    else:
                        st.error("No data to create table. Upload an Excel file.")
            else:
                st.error("Failed to load data from Excel file. Ensure the file is in the correct format.")
        else:
            st.info("Upload an Excel file to preview and create a table.")  # Instruction for the user

    with col2:
        st.subheader("Data Preview and SQL Tables")

        if 'excel_df' in st.session_state:
            df = st.session_state["excel_df"]
            st.write("Preview of Uploaded Data:")
            st.dataframe(df.head())  # Show data head

        if "sql_tables" in st.session_state:
            st.write("SQL Tables:")
            st.write(st.session_state["sql_tables"])  # Display SQL tables

def save_database_button(conn):
    """Handles database download functionality."""

    db_bytes = save_database(conn)
    if db_bytes:
        st.download_button(
            label="Download Database",
            data=db_bytes,
            file_name="chat_data.db",
            mime="application/vnd.sqlite3",
        )
def handle_sqlite_upload(file, conn):
    """Processes SQLite file upload."""
    table_names = load_sqlite_data(file, conn)
    if table_names:
        st.subheader("Tables in Database:")
        st.write(table_names)
def data_upload_tab(conn):
    """Handles the Data Upload tab."""
    col1, col2 = st.columns(2)
    with col1:
        st.header("Data Upload")
        uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
        sqlite_file = st.file_uploader("Upload SQLite database", type=["db", "sqlite"])

        if st.sidebar.button("Save Database"):
            save_database_button(conn)


    if uploaded_file:
        create_sql_button = st.button("Create SQL table from Excel data")
        handle_excel_upload(uploaded_file, conn,create_sql_button,col1, col2)

    if sqlite_file:
        handle_sqlite_upload(sqlite_file, conn)

