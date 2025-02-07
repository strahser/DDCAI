
import streamlit as st
import pandas as pd
from PageData.DB.database import execute_sql
from multipage_streamlit import State

from PageData.utils import execute_python_code, get_common_vars


def data_analysis_tab(conn):
    """Handles the combined SQL and Python Data View tab."""
    st.header("Data Analysis")
    # Include 'code' column in the initial query
    code_snippets = execute_sql("SELECT id, name, type, code, category FROM code_snippets", conn)

    if isinstance(code_snippets, pd.DataFrame): # Check if code_snippets is a DataFrame
        if not code_snippets.empty:
            # Get unique categories and handle the tab structure
            categories = code_snippets['category'].unique()
            # Sidebar selections *before* tabs are created
            selected_python_ids, selected_sql_tables = get_sidebar_selections(code_snippets)

            if len(categories) > 1 or (len(categories) == 1 and pd.isna(categories[0])): # Display tabs only if more than 1 category, or if there is a default category
                tab_names = [cat if not pd.isna(cat) else "default" for cat in categories] # Replace NaN with 'default'
                tabs = st.tabs(tab_names)

                for i, category in enumerate(categories):
                    with tabs[i]:
                        cat_snippets = code_snippets[code_snippets['category'] == category]
                        if pd.isna(category):
                            cat_snippets = code_snippets[code_snippets['category'].isna()] # Use nan value
                        st.subheader(f"Category: {category if not pd.isna(category) else 'default'}")

                        # Filter snippets by type and category, and display
                        display_snippets(cat_snippets, conn, selected_python_ids, selected_sql_tables)
            else:
                # if only default category is present we show data as before
                st.subheader(f"Category: default")
                display_snippets(code_snippets, conn, selected_python_ids, selected_sql_tables)
        else:
            st.info("No saved code snippets available.")
    else:
        st.error(f"Error retrieving code snippets: {code_snippets}")


def get_sidebar_selections(code_snippets):
    """Displays multiselect widgets in the sidebar and returns selections."""
    state = State(__name__)
    python_snippets = code_snippets[code_snippets["type"] == "python"]
    sql_snippets = code_snippets[code_snippets["type"] == "sql"]

    selected_python_ids = []
    selected_sql_tables = []

    if not python_snippets.empty:
        selected_python_ids = st.sidebar.multiselect(
            "Select Python scripts to execute",
            python_snippets.index.tolist(),
            format_func=lambda x: f"{python_snippets.loc[x, 'name']} (Python)",
            key=state("sidebar_python_select")
        )

    if not sql_snippets.empty:
        tables = [x for x in sql_snippets['name'].tolist()]
        selected_sql_tables = st.sidebar.multiselect(
            "Select SQL tables/views to display",
            tables,
            key=state("sidebar_sql_select")
        )

    return selected_python_ids, selected_sql_tables


def display_snippets(snippets, conn, selected_python_ids, selected_sql_tables):
    """Displays Python and SQL snippets based on sidebar selections."""
    python_snippets = snippets[snippets["type"] == "python"]
    sql_snippets = snippets[snippets["type"] == "sql"]

    # Execute selected Python snippets
    for code_id in selected_python_ids:
        if code_id in python_snippets.index:  # Check if ID is in this category
            code = python_snippets.loc[code_id, 'code']
            if code:
                with st.expander(f"Executing: {python_snippets.loc[code_id, 'name']}"):
                    output, error = execute_python_code(code, get_common_vars())
                    if error:
                        st.error(f"Execution error: {error}")
                    else:
                        st.text(output or "No output generated")

    # Display selected SQL views
    for table in selected_sql_tables:
        if table in sql_snippets['name'].values:  # Check if table name is in this category
            with st.expander(f"Executing sql: {table}"):
                sql_snippet = sql_snippets[sql_snippets["name"] == table]
                data = execute_sql(sql_snippet['code'].iloc[0], conn)
                if isinstance(data, pd.DataFrame):
                    st.dataframe(data)
                else:
                    st.error(f"Failed to load data from {table}")