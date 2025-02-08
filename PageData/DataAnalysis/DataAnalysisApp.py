import json
import sqlite3

import streamlit as st
import pandas as pd
from PageData.DB.database import execute_sql
from PageData.utils import execute_python_code, get_common_vars


class DataAnalysisApp:
    def __init__(self, conn):  # Changed to persistent DB
        self.conn = conn

        # Initialize session state

    def data_analysis_tab_run(self):
        """Handles the combined SQL and Python Data View tab."""
        st.header("Data Analysis")

        # Retrieve code snippets
        code_snippets = execute_sql("SELECT id, name, type, code, category FROM code_snippets", self.conn)

        if isinstance(code_snippets, pd.DataFrame):  # Check if code_snippets is a DataFrame
            if not code_snippets.empty:
                # Get unique categories and handle the tab structure
                categories = code_snippets['category'].unique()

                # Get sidebar selections *before* tabs are created
                selected_python_ids, selected_sql_tables = self.get_sidebar_selections(code_snippets)

                if len(categories) > 1 or (len(categories) == 1 and pd.isna(
                        categories[0])):  # Display tabs only if more than 1 category, or if there is a default category
                    tab_names = [cat if not pd.isna(cat) else "default" for cat in
                                 categories]  # Replace NaN with 'default'
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
                            self.display_snippets(cat_snippets, selected_python_ids, selected_sql_tables)
                else:
                    # if only default category is present we show data as before
                    st.subheader(f"Category: default")
                    self.display_snippets(code_snippets, selected_python_ids, selected_sql_tables)
            else:
                st.info("No saved code snippets available.")
        else:
            st.error(f"Error retrieving code snippets: {code_snippets}")

    def get_sidebar_selections(self, code_snippets):
        """Displays multiselect widgets and save/load buttons in the sidebar."""

        python_snippets = code_snippets[code_snippets["type"] == "python"]
        sql_snippets = code_snippets[code_snippets["type"] == "sql"]

        try:
            # Multiselect widgets with fixed keys
            selected_python_ids = st.sidebar.multiselect(
                "Select Python scripts to execute",
                options=python_snippets.index.tolist() if not python_snippets.empty else [],
                default=st.session_state.global_python_select,
                format_func=lambda x: f"{python_snippets.loc[x, 'name']} (Python)",
                key="selected_python_ids"
            )
        except:
            selected_python_ids = st.sidebar.multiselect(
                "Select Python scripts to execute",
                options=python_snippets.index.tolist() if not python_snippets.empty else [],
                format_func=lambda x: f"{python_snippets.loc[x, 'name']} (Python)",
                key="selected_python_ids"
            )
            st.warning("Can not load selected python scripts, please check if you delete them?")
        try:
            selected_sql_tables = st.sidebar.multiselect(
                "Select SQL tables/views to display",
                options=sql_snippets['name'].tolist() if not sql_snippets.empty else [],
                default=st.session_state.global_sql_select,
                key="selected_sql_tables"
            )
        except:
            selected_sql_tables = st.sidebar.multiselect(
                "Select SQL tables/views to display",
                options=sql_snippets['name'].tolist() if not sql_snippets.empty else [],
                key="selected_sql_tables"
            )
            st.warning("Can not load selected SQL tables, please check if you delete them?")
        # Save/Load buttons
        col1, col2 = st.sidebar.columns(2)
        # Use the updated call backs without the db connect.
        if col1.button("💾 Save Selections"):
            self.save_button_callback(selected_python_ids, selected_sql_tables)
        if col2.button("📂 Load Selections"):
            self.load_button_callback()

        return selected_python_ids, selected_sql_tables

    def display_snippets(self, snippets, selected_python_ids, selected_sql_tables):
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
                    data = execute_sql(sql_snippet['code'].iloc[0], self.conn)  # Use database connection's execute_sql
                    if isinstance(data, pd.DataFrame):
                        st.dataframe(data)
                    else:
                        st.error(f"Failed to load data from {table}")

    def save_selections(self, python_ids, sql_tables):
        """Saves the current selections to the database."""
        try:
            data = {
                "python_ids": python_ids,
                "sql_tables": sql_tables
            }
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_settings
                (user_id, setting_name, setting_value)
                VALUES (?, ?, ?)
            """, ("default", "selections", json.dumps(data)))
            self.conn.commit()
            st.sidebar.success("settings saved!")
        except Exception as e:
            st.sidebar.error(f"error saved: {str(e)}")

    def load_selections(self):
        """Loads saved settings from the database."""
        try:
            cursor = self.conn.cursor()
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

    def save_button_callback(self, python_ids, sql_tables):
        """Callback function for the save button."""
        self.save_selections(python_ids, sql_tables)  # Use class method
        st.session_state.global_python_select = python_ids
        st.session_state.global_sql_select = sql_tables

    def load_button_callback(self):
        """Callback function for the load button."""
        python_ids, sql_tables = self.load_selections()  # Use class method

        st.session_state.global_python_select = python_ids
        st.session_state.global_sql_select = sql_tables
        st.session_state.global_key = not st.session_state.get("global_key", False)  # force re-render
        st.rerun()  # force re-render
