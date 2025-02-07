import streamlit as st



class AdminTab:
    """Base class for tabs with editable tables."""

    def __init__(self, conn, title):
        """
        Initializes the AdminTab.

        Args:
            conn: Database connection object.
            title (str): Title of the tab.
        """
        self.conn = conn
        self.title = title
        self.data = None

    def display_header(self):
        """Displays the tab header."""
        st.header(self.title)

    def load_data(self):
        """Loads data from the database. Must be implemented in child classes."""
        raise NotImplementedError

    def get_column_config(self):
        """Returns the column configuration for st.data_editor."""
        raise NotImplementedError

    def delete_entry(self, row):
        """Deletes an entry. Must be implemented in child classes."""
        raise NotImplementedError

    def update_entry(self, row):
        """Updates an entry. Must be implemented in child classes."""
        raise NotImplementedError

    def display_editor(self):
        """Displays the data editor and returns the edited data."""
        if self.data is not None and not self.data.empty:
            self.data['delete'] = False
            edited_data = st.data_editor(
                self.data,
                column_config=self.get_column_config(),
                key=f"{self.title}_editor",
                hide_index=True,
            )
            return edited_data
        else:
            st.info("No data found.")
            return None

    def handle_changes(self, edited_data):
        """Handles data changes."""
        if edited_data is not None and st.button("Apply Changes"):
            for _, row in edited_data.iterrows():
                if row["delete"]:
                    self.delete_entry(row)
                else:
                    self.update_entry(row)
            st.success("Changes Applied")

    def display(self):
        """Main method to display the entire tab."""
        self.display_header()
        self.load_data()
        edited_data = self.display_editor()
        self.handle_changes(edited_data)
