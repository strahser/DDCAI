
import streamlit as st

from PageData.Admin.ApiKeysTab import ApiKeysTab
from PageData.Admin.CodeSnippetsTab import CodeSnippetsTab
from PageData.Admin.ViewsTab import ViewsTab


def admin_panel(conn):
    """The main function is to display the admin panel.."""
    st.title("Admin Panel")
    tab1, tab2, tab3 = st.tabs(["Code Snippets", "Views", "API Keys"])

    with tab1:
        CodeSnippetsTab(conn).display()

    with tab2:
        ViewsTab(conn).display()

    with tab3:
        ApiKeysTab(conn).display()