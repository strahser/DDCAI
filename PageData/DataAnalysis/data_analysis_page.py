
import streamlit as st
import pandas as pd
from PageData.DB.database import execute_sql
from PageData.utils import get_common_vars, execute_python_code
from multipage_streamlit import State

def handle_snippets_by_type(snippets, conn):
    """Handles displaying python and sql snippets."""
    if not snippets.empty:
        python_snippets = snippets[snippets["type"] == "python"]
        sql_snippets = snippets[snippets["type"] == "sql"]
        if not python_snippets.empty:
             handle_python_snippets(python_snippets, conn)
        if not sql_snippets.empty:
            handle_sql_views(conn, sql_snippets)
def data_analysis_tab(conn):
    """Handles the combined SQL and Python Data View tab."""
    st.header("Data Analysis")
    # Include 'code' column in the initial query
    code_snippets = execute_sql("SELECT id, name, type, code, category FROM code_snippets", conn)

    if isinstance(code_snippets, pd.DataFrame): # Check if code_snippets is a DataFrame
        if not code_snippets.empty:
            # Get unique categories and handle the tab structure
            categories = code_snippets['category'].unique()
            if len(categories) > 1 or (len(categories) == 1 and pd.isna(categories[0])): # Display tabs only if more than 1 category, or if there is a default category
                tab_names = [cat if not pd.isna(cat) else "default" for cat in categories] # Replace NaN with 'default'
                tabs = st.tabs(tab_names)

                for i, category in enumerate(categories):
                    with tabs[i]:
                        cat_snippets = code_snippets[code_snippets['category'] == category]
                        if pd.isna(category):
                            cat_snippets = code_snippets[code_snippets['category'].isna()] # Use nan value
                        st.subheader(f"Category: {category if not pd.isna(category) else 'default'}")
                        handle_snippets_by_type(cat_snippets, conn)
            else:
                # if only default category is present we show data as before
                st.subheader(f"Category: default")
                handle_snippets_by_type(code_snippets, conn)
        else:
            st.info("No saved code snippets available.")
    else:
        st.error(f"Error retrieving code snippets: {code_snippets}")

def handle_python_snippets(snippets, conn):
    state = State(__name__)
    """Handles Python code snippet execution."""
    # Set 'id' as index and include 'code' column in the query
    python_snippets = snippets[snippets["type"] == "python"].set_index('id')

    selected_ids = st.sidebar.multiselect(
        "Select Python scripts to execute",
        python_snippets.index.tolist(),  # Use index values directly
        format_func=lambda x: f"{python_snippets.loc[x, 'name']} (Python)",
        key=state("handle_python_snippets_selected_ids")
    )

    for code_id in selected_ids:
        # Get code directly from the dataframe (no extra database query needed)
        code = python_snippets.loc[code_id, 'code']
        if code:
            with st.expander(f"Executing: {python_snippets.loc[code_id, 'name']}"):
                output, error = execute_python_code(code, get_common_vars())
                if error:
                    st.error(f"Execution error: {error}")
                else:
                    st.text(output or "No output generated")

def handle_sql_views(conn, snippets):
    """Handles SQL view display."""
    state = State(__name__)
    python_snippets = snippets
    tables = [x for x in python_snippets['name'].tolist()]

    selected_tables = st.sidebar.multiselect("Select sql tables/views to display", tables,key=state("handle_sql_views_selected_tables"))

    for table in selected_tables:
        with st.expander(f"Executing sql: {table}"):
            sql_snippet = python_snippets[python_snippets["name"] == table]
            data = execute_sql(sql_snippet['code'].iloc[0], conn)
            if isinstance(data, pd.DataFrame):
                st.dataframe(data)
            else:
                st.error(f"Failed to load data from {table}")

