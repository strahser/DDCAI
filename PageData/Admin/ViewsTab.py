import pandas as pd
import streamlit as st

from PageData.Admin.Utils.DbUtils import create_code_snippet
from PageData.DB.database import delete_view_by_name
from streamlit_ace import st_ace, THEMES

class ViewsTab:
    """Tab for managing SQL views."""

    def __init__(self, conn):
        """
        Initializes the ViewsTab.

        Args:
            conn: Database connection object.
        """
        self.conn = conn

    def display(self):
        """Displays the entire tab."""
        st.header("View Management")
        self._display_create_form()
        self._display_existing_views()

    def _display_create_form(self):
        """Form for creating a new view."""
        with st.form("create_view_form"):
            view_name = st.text_input("View Name")
            view_code =  st_ace(
            value= "SELECT * FROM _df LIMIT 10;",
            placeholder="Type SQL Query",
            language="sql",
            theme=THEMES.index("xcode"),
            key="sql_code"
        )
            if st.form_submit_button("Create View"):
                create_code_snippet(
                    self.conn,
                    type_="sql",
                    code=view_code,
                    name=view_name,
                    is_view=True
                )

    def _display_existing_views(self):
        """Displays a list of existing views."""

        # Mock database interaction (replace with your actual database interaction)
        # This is a simplified example; your actual code will query the database.
        mock_views = [("view1",), ("view2",), ("view3",)] # Example  List of tuples.
        #

        if mock_views:
            df = pd.DataFrame(mock_views, columns=["View Name"])
            df["Delete"] = False

            edited_df = st.data_editor(
                df,
                column_config={
                    "View Name": st.column_config.TextColumn(disabled=True),
                    "Delete": st.column_config.CheckboxColumn()
                },
                key="views_editor",
                hide_index=True,
            )

            if st.button("Apply View Changes"):
                for _, row in edited_df.iterrows():
                    if row["Delete"]:
                        delete_view_by_name(self.conn, row["View Name"])
                st.success("Views updated")
        else:
            st.info("No views found")