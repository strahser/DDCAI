import json
import sqlite3

import streamlit as st
import pandas as pd
from PageData.DB.database import execute_sql
from multipage_streamlit import State
from PageData.utils import execute_python_code, get_common_vars


def data_analysis_tab():
    """Handles the combined SQL and Python Data View tab."""
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    st.header("Data Analysis")
    # Include 'code' column in the initial query
    code_snippets = execute_sql("SELECT id, name, type, code, category FROM code_snippets", conn)

    if isinstance(code_snippets, pd.DataFrame): # Check if code_snippets is a DataFrame
        if not code_snippets.empty:
            # Get unique categories and handle the tab structure
            categories = code_snippets['category'].unique()

            # Get sidebar selections *before* tabs are created
            selected_python_ids, selected_sql_tables = get_sidebar_selections(code_snippets)

            if len(categories) > 1 or (len(categories) == 1 and pd.isna(categories[0])): # Display tabs only if more than 1 category, or if there is a default category
                tab_names = [cat if not pd.isna(cat) else "default" for cat in categories] # Replace NaN with 'default'
                tabs = st.tabs(tab_names)

                for i, category in enumerate(categories):
                    with tabs[i]:
                        # Filter snippets by type and category
                        if pd.isna(category):
                            cat_snippets = code_snippets[code_snippets['category'].isna()]
                        else:
                            cat_snippets = code_snippets[code_snippets['category'] == category]


                        st.subheader(f"Category: {category if not pd.isna(category) else 'default'}")

                        # Filter snippets by type and category, and display
                        display_snippets(cat_snippets,  selected_python_ids, selected_sql_tables)
            else:
                # if only default category is present we show data as before
                st.subheader(f"Category: default")
                display_snippets(code_snippets,  selected_python_ids, selected_sql_tables)
        else:
            st.info("No saved code snippets available.")
    else:
        st.error(f"Error retrieving code snippets: {code_snippets}")


def get_sidebar_selections(code_snippets):
    """Displays multiselect widgets and save/load buttons in the sidebar."""
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    python_snippets = code_snippets[code_snippets["type"] == "python"]
    sql_snippets = code_snippets[code_snippets["type"] == "sql"]

    # Initialize session state variables if they don't exist
    if 'global_python_select' not in st.session_state:
        st.session_state.global_python_select = []
    if 'global_sql_select' not in st.session_state:
        st.session_state.global_sql_select = []

    # Multiselect widgets with fixed keys
    selected_python_ids = st.sidebar.multiselect(
        "Select Python scripts to execute",
        options=python_snippets.index.tolist() if not python_snippets.empty else [],
        default=st.session_state.global_python_select,
        format_func=lambda x: f"{python_snippets.loc[x, 'name']} (Python)",
        key="global_python_select"
    )

    selected_sql_tables = st.sidebar.multiselect(
        "Select SQL tables/views to display",
        options=sql_snippets['name'].tolist() if not sql_snippets.empty else [],
        default=st.session_state.global_sql_select,
        key="global_sql_select"
    )

    # Save/Load buttons
    col1, col2 = st.sidebar.columns(2)
    if col1.button("💾 Save Selections", on_click=save_button_callback, args=(st.session_state.global_python_select, st.session_state.global_sql_select)):
        pass
    if col2.button("📂 Load Selections", on_click=load_button_callback):
        pass

    return selected_python_ids, selected_sql_tables


def display_snippets(snippets,  selected_python_ids, selected_sql_tables):
    """Displays Python and SQL snippets based on sidebar selections."""
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
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

def save_selections( python_ids, sql_tables):
    """Saves the current selections to the database."""
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    try:
        data = {
            "python_ids": python_ids,
            "sql_tables": sql_tables
        }
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_settings
            (user_id, setting_name, setting_value)
            VALUES (?, ?, ?)
        """, ("default", "selections", json.dumps(data)))
        conn.commit()
        st.sidebar.success("settings saved!")
    except Exception as e:
        st.sidebar.error(f"error saved: {str(e)}")

def load_selections():
    """Loads saved settings from the database."""
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT setting_value FROM user_settings
            WHERE user_id = ? AND setting_name = ?
        """, ("default", "selections"))
        result = cursor.fetchone()
        if result:
            data = json.loads(result[0])
            return data.get("python_ids", []), data.get("sql_tables", [])
        return [], []
    except Exception as e:
        st.sidebar.error(f"error loaded: {str(e)}")
        return [], []

def save_button_callback( python_ids, sql_tables):
    """Callback function for save button."""
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    save_selections( python_ids, sql_tables)

def load_button_callback():
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    """Callback function for load button."""
    loaded_python, loaded_sql = load_selections()
    st.session_state.global_python_select = loaded_python
    st.session_state.global_sql_select = loaded_sql
    st.rerun()