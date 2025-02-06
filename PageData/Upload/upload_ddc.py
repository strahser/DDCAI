import streamlit as st
import os
import subprocess
import pandas as pd





def load_excel_data(uploaded_file):
    """Loads data from an uploaded Excel file."""
    try:
        df = pd.read_excel(uploaded_file)
        # Find duplicate column names
        seen_cols = set()
        duplicate_cols = []
        original_cols = df.columns.tolist()  # make it list for the purposes of this scope
        for col in original_cols:
            if col in seen_cols:
                duplicate_cols.append(col)
            else:
                seen_cols.add(col)
        # Handle duplicate column names
        if duplicate_cols:
            st.warning("The Excel file contains duplicate column names. Please fix these in the Excel file.")
            st.write("Duplicate columns:", duplicate_cols)
            return None

        st.success("Excel file loaded successfully!")
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

def convert_revit_data(path_conv, file_path):
    """Converts Revit data using the DDC converter.

    Args:
        path_conv: Path to the DDC converter folder.
        file_path: Path to the Revit file.

    Returns:
         pandas DataFrame: The converted DataFrame or None if an error occurs.
    """

    try:
        with st.spinner("Converting Revit file..."):
            process = subprocess.Popen(
                [os.path.join(path_conv, 'RvtExporter.exe'), file_path],
                cwd=path_conv,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                st.success("Conversion finished")
                output_file = file_path[:-4] + "_rvt.xlsx"
                df = pd.read_excel(output_file)
                # df.columns = [col.split(' : ')[0] for col in df.columns]  # remove storage type does not work in streamlit visualisation
                st.success("Revit data successfully loaded!")
                return df
            else:
                 st.error(f"Conversion failed. Error message: {stderr.decode('utf-8')}")
                 return None
    except Exception as e:
        st.error(f"Error during Revit conversion: {e}")
        return None

def upload_ddc():
    st.title("Data Upload")
    data_source = st.radio("Select Data Source", ["Excel File", "Revit Converter"])
    if data_source == "Excel File":
        uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")
        if uploaded_file is not None:
            df = load_excel_data(uploaded_file)
            if df is not None:
                st.session_state["excel_df"] = df

    elif data_source == "Revit Converter":
        base_path_conv_path = r"e:\DDC"
        base_revit_file_path = r"e:\DDC\2022 rstadvancedsampleproject.rvt"
        st.subheader("Enter DDC Folder and Revit File Path")
        path_conv = st.text_input("Enter path to DDC converter folder (where RvtExporter.exe is located)", base_path_conv_path)  # DDC folder path via text input
        file_path = st.text_input("Enter path to Revit file (.rvt)", base_revit_file_path)# Revit file path by text input

        if st.button("Convert Revit File"):
            if file_path and path_conv:
                df = convert_revit_data(path_conv, file_path)
                if df is not None:
                    st.session_state["excel_df"] = df
            else:
                st.warning("Please enter DDC converter folder and Revit file path.")

