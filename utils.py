import re
import matplotlib.pyplot as plt #Added import
import pandas as pd
import streamlit as st
import seaborn as sns
def sanitize_column_name(name: str) -> str:
    """Sanitizes a column name for use in SQLite."""
    name = re.sub(r"[^a-zA-Z0-9_ ]", "", name)
    name = name.replace(" ", "_")
    name = re.sub(r"^[^a-zA-Z_]+", "_", name)
    return name

import pandas as pd
from io import StringIO
import sys

def execute_python_code(code, local_vars):
    """Executes Python code in a controlled environment."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    try:
        exec(code, globals(), local_vars)
        return captured_output.getvalue()
    except Exception as e:
        return f"Error executing code: {str(e)}"
    finally:
        sys.stdout = old_stdout

def get_common_vars():
    """Returns a dictionary of commonly used variables."""
    return {
        "st": st,
        "pd": pd,
        "plt": plt,
        "sns": sns,
    }

