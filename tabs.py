import streamlit as st
import uuid
from io import StringIO
import pandas as pd
import sys

from database import create_view, execute_sql, insert_code_snippet, delete_code_snippet, get_table_names, \
    execute_sql_text
from data_loader import load_excel_data, load_sqlite_data, create_sql_table  # Moved from within functions
from llm import initialize_llm # Moved from within functions
from chat_logic import process_chat_prompt # Moved from within functions


class CodeExecutionTab:
    def __init__(self, conn):
        self.conn = conn
        self.sql_code = "SELECT * FROM _df LIMIT 10;"
        self.python_code = ("df = st.session_state.get('excel_df')\n"
                            "if df is not None:\n"
                            "    st.write(df.head())\n"
                            "else:\n"
                            "    st.write('No dataframe loaded. Please upload data.')")
        self.sql_code_name = "Untitled SQL Script"
        self.python_code_name = "Untitled Python Script"
        self.view_name = "Untitled View"

    def display(self):
        """Displays the Code Execution tab."""
        st.header("Code Execution")

        col1, col2 = st.columns(2)
        with col1:
            with st.form(key="sql_form"):
                self.sql_code = st.text_area("SQL Code", value=self.sql_code, height=200)
                col1a, col1b, col1c = st.columns([2, 1, 2])
                with col1a:
                    self.sql_code_name = st.text_input("Script Name:", value=self.sql_code_name)
                with col1b:
                    save_sql = st.form_submit_button("Save SQL")
                with col1c:
                    self.view_name = st.text_input("View Name:", value=self.view_name)
                create_view_button = st.form_submit_button("Create View")

                if save_sql:
                    insert_code_snippet(self.conn, "sql", self.sql_code, self.sql_code_name)
                if create_view_button:
                    insert_code_snippet(self.conn, "sql", self.sql_code, self.sql_code_name, is_view=True)
                    view_result = create_view(self.sql_code, self.conn, self.view_name)
                    if isinstance(view_result, str):
                        st.error(f"View creation failed: {view_result}")

                if st.form_submit_button("Execute SQL"):
                    result = create_view(self.sql_code, self.conn)
                    if isinstance(result, pd.DataFrame):
                        st.dataframe(result)
                    else:
                        st.error(f"View creation failed: {result}")

        with col2:
            with st.form(key="python_form"):
                self.python_code = st.text_area("Python Code",
                                             value=self.python_code,
                                             height=200)
                col2a, col2b = st.columns([2,1])
                with col2a:
                    self.python_code_name = st.text_input("Script Name:", value=self.python_code_name)

                with col2b:
                    save_python = st.form_submit_button("Save Python")
                if save_python:
                    insert_code_snippet(self.conn, "python", self.python_code, self.python_code_name)
                if st.form_submit_button("Execute Python"):
                    try:
                        old_stdout = sys.stdout
                        sys.stdout = captured_output = StringIO()
                        local_vars = {"st": st, "pd": pd, "df": st.session_state.get("excel_df")}
                        exec(self.python_code, globals(), local_vars) #Now using local vars
                        st.text(captured_output.getvalue())
                        sys.stdout = old_stdout
                    except Exception as e:
                        st.error(f"Error executing Python code: {str(e)}")

        # Display code snippets and views
        st.subheader("Saved Scripts")
        scripts = execute_sql("SELECT id, name, type, is_view FROM code_snippets", self.conn)
        if scripts is not None and not scripts.empty:
            st.dataframe(scripts)
        else:
            st.info("No saved scripts available.")
        # Display the views which exist

        st.subheader("Saved Views")
        table_names = get_table_names(self.conn) #Getting names of the table names
        view_names = [name for name in table_names if name not in st.session_state.get("sql_tables", [])] #Display if they are not in the tables
        st.write(view_names)

def data_upload_tab(conn):
    """Handles the Data Upload tab."""
    st.header("Data Upload")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    sqlite_file = st.file_uploader("Upload SQLite database", type=["db", "sqlite"])
    preview_table = st.empty()
    show_existing_tables = st.checkbox("Show Existing Tables Before Loading Excel")

    if show_existing_tables:
        available_tables = get_table_names(conn)
        st.write("Existing Tables:")
        st.write(available_tables)
    # Check session_state before loading excel files
    if uploaded_file is not None:
        if "uploaded_file_name" not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
            st.session_state.uploaded_file_name = uploaded_file.name
            df = load_excel_data(uploaded_file, conn)
            if df is not None:
                st.session_state["excel_df"] = df
                st.subheader("Preview of Uploaded Data:")
                st.dataframe(df.head())
                if st.button("Create SQL table from Excel data"):
                    if create_sql_table(df, conn):
                        st.success("SQL table created successfully!")
                        st.session_state["sql_tables"] = get_table_names(conn)
                    else:
                        st.error("Failed to create SQL table.")
    if sqlite_file:
        table_names = load_sqlite_data(sqlite_file, conn)
        if table_names:
            with preview_table.container():
                st.subheader("Table names in database:")
                st.write(table_names)

def chat_with_ai_tab(conn):
    """Handles the Chat with AI tab."""
    st.title("AI Data Analyst Chat")
    st.write("Enter your question below:")
    llm_choice = st.sidebar.radio("Choose LLM", ["Local", "Cloud"])
    api_key = None
    cloud_model = None
    if llm_choice == "Cloud":
        cloud_model = st.sidebar.selectbox("Select Cloud Model", ["OpenAI", "Groq", "Anthropic"])
        api_key = st.sidebar.text_input(f"API Key for {cloud_model}", type="password")

    llm = initialize_llm(llm_choice, api_key, cloud_model)
    df = st.session_state.get("excel_df")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Your question", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Processing..."):
            response = process_chat_prompt(prompt, df, llm)  # Pass LLM instead of df
        with st.chat_message("assistant"):
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    if st.sidebar.checkbox("Show History"):
        history = execute_sql("SELECT question, answer, timestamp FROM chat_history", conn)
        st.sidebar.dataframe(history)

    if st.sidebar.button("Save Database"):
        from .database import save_database
        db_bytes = save_database(conn)
        if db_bytes:
            st.sidebar.download_button(
                label="Download SQLite Database",
                data=db_bytes,
                file_name="chat_data.db",
                mime="application/vnd.sqlite3",
            )

def data_analysis_tab(conn):
    """Handles the combined SQL and Python Data View tab."""
    st.header("Data Analysis")

    # Display code snippets table
    code_snippets = execute_sql("SELECT id, name, type, is_view FROM code_snippets", conn)
    if code_snippets is not None and not code_snippets.empty:
        # filter code snippets
        python_code_snippets = code_snippets[code_snippets["type"] == "python"]
        st.dataframe(code_snippets)
        st.subheader("Select Scripts to Execute")
        #User selected Code Snippet

        selected_codes = st.multiselect("Select code snippets to execute", python_code_snippets["id"].tolist(),
                                         format_func=lambda x: f"{python_code_snippets[python_code_snippets['id'] == x]['name'].iloc[0]} ({python_code_snippets[python_code_snippets['id'] == x]['type'].iloc[0]})") #Fixes error if the code_snippet is not a value
        # Python code execution
        st.subheader("Python Code Execution")

        for code_id in selected_codes:
            code_info = python_code_snippets[python_code_snippets["id"] == code_id]
            if not code_info.empty and code_info["type"].iloc[0] == "python":
                code_name = code_info["name"].iloc[0]
                # code = execute_sql(f"SELECT code FROM code_snippets WHERE id = '{code_id}'", conn) # this was causing issues, and I will address it directly
                python_code = execute_sql_text(f"SELECT code FROM code_snippets WHERE id = '{code_id}'", conn)

                # python_code = code[0][0] #fixes the other one
                if python_code is None:
                    st.error(f"Could not load Python code snippet with ID {code_id}.")
                    continue
                with st.expander(f"Python Code: {code_name}"):
                    try:
                        old_stdout = sys.stdout
                        sys.stdout = captured_output = StringIO()
                        local_vars = {"st": st, "pd": pd, "df": st.session_state.get("excel_df")} #This has been added for great access of data at any time.
                        exec(python_code, globals(), local_vars)
                        st.write("Output:")
                        st.text(captured_output.getvalue())
                        sys.stdout = old_stdout
                    except Exception as e:
                        st.error(f"Error executing Python code: {str(e)}")
        # SQL data view
        st.subheader("SQL Data View")
        available_tables = get_table_names(conn)
        selected_tables = st.multiselect("Select tables and views:", available_tables)
        for table_name in selected_tables:
            try:
                data = execute_sql(f"SELECT * FROM '{table_name}'", conn) #fixes the issue of no tables existing and it not loading
                st.dataframe(data)
            except Exception as e:
                st.error(f"Error displaying table '{table_name}': {e}")
        if not selected_codes and not selected_tables:
            st.info("Select python snippets or code snippets to get started!")
    else:
        st.info("No saved Python code snippets available. Add some in 'Code Execution' tab.")