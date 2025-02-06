import re
import matplotlib.pyplot as plt #Added import
import pandas as pd
import streamlit as st
import seaborn as sns
from io import StringIO
import sys
def sanitize_column_name(name: str) -> str:
    """Sanitizes a column name for use in SQLite."""
    name = re.sub(r"[^a-zA-Z0-9_ ]", "", name)
    name = name.replace(" ", "_")
    name = re.sub(r"^[^a-zA-Z_]+", "_", name)
    return name


def execute_python_code(code, local_vars=None):
    """Executes Python code and captures output/errors."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    try:
        exec(code, globals(), local_vars or {})
        return captured_output.getvalue(), None
    except Exception as e:
        return None, str(e)
    finally:
        sys.stdout = old_stdout


def get_common_vars():
    """Returns commonly used variables for code execution."""
    return {
        "st": st,
        "pd": pd,
        "df": st.session_state.get("excel_df"),
        "plt": plt
    }

