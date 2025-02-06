import pandas as pd
import sqlite3
import streamlit as st


def create_sql_table(df: pd.DataFrame, conn: sqlite3.Connection, table_name: str = "_df") -> bool:
    """Creates an SQL table from a Pandas DataFrame, attempting different methods."""
    try:
        # 1. Attempt direct table creation using pandas to_sql
        try:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            st.success("SQL table created successfully using pandas to_sql!")
            st.session_state["excel_df"] = df
            return True
        except Exception as e:
            st.warning(f"Failed to create table using pandas to_sql: {e}. Attempting manual table creation.")

        # 2. Manual table creation
        cursor = conn.cursor()

        # Create the base table structure
        cursor.execute(f"CREATE TABLE IF NOT EXISTS \"{table_name}\" (index_col INTEGER PRIMARY KEY)")
        conn.commit()

        # Add columns one by one with renaming on conflict
        renamed_columns = {}  # Track renamed columns
        skipped_columns = []
        for original_col in df.columns:
            col = original_col  # Added to keep value alive

            try:
                dtype = df[col].dtype
                if pd.api.types.is_integer_dtype(dtype):
                    sql_dtype = "TEXT"  # Changed to Text so that it does not throw the error
                elif pd.api.types.is_float_dtype(dtype):
                    sql_dtype = "REAL"
                elif pd.api.types.is_datetime64_any_dtype(dtype):
                    sql_dtype = "TEXT"  # Store datetimes as TEXT
                else:
                    sql_dtype = "TEXT"  # Default to TEXT for other types

                add_column_sql = f"ALTER TABLE \"{table_name}\" ADD COLUMN \"{col}\" {sql_dtype}"
                cursor.execute(add_column_sql)
                conn.commit()
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    # Attempt renaming the column
                    new_col = f"{col}_renamed"
                    try:
                        add_column_sql = f"ALTER TABLE \"{table_name}\" ADD COLUMN \"{new_col}\" {sql_dtype}"
                        cursor.execute(add_column_sql)
                        conn.commit()
                        # Track successful renaming
                        renamed_columns[original_col] = new_col
                        # Update the DataFrame with the new column name
                        df.rename(columns={col: new_col}, inplace=True)
                        col = new_col  # this now must be updated!
                    except Exception as e2:
                        st.warning(f"Failed to rename and add column '{col}': {e2}. Skipping column.")
                        skipped_columns.append(col)
                        conn.rollback()
                        continue  # this must continue to the next one
                else:
                    st.error(f"Error adding column '{col}': {e}")
                    conn.rollback()
                    return False
            except Exception as e:
                st.error(f"Error adding column '{col}': {e}")
                conn.rollback()
                return False  # Stop on other errors

        # Inform about skipped or renamed columns
        if skipped_columns:
            st.warning(f"The following columns were skipped due to errors: {skipped_columns}")
            for skipped_column in skipped_columns:  # Remove those columns
                df.drop(columns=skipped_column, inplace=True)
                # I will need to keep in mind the original file!
        if renamed_columns:
            st.info(f"The following columns were automatically renamed: {renamed_columns}")
        # Check for data before proceeding
        if df.empty:
            st.warning("DataFrame is empty after dropping rows and columns with missing values. Cannot create SQL table.")
            return False

        # Populate the table with the data
        for index, row in df.iterrows():
            try:
                # Convert large integers to strings
                values = [str(index)] + [str(val) if isinstance(val, int) and abs(val) > 2**63 else val for val in row.tolist()]  # Changed to row.to_numpy() and index to now just use the data, as there is an index col and it is auto.
                placeholders = ", ".join("?" for _ in values)  # One placeholder for each value
                insert_sql = f"INSERT INTO \"{table_name}\" VALUES ({placeholders})"
                cursor.execute(insert_sql, values)
                conn.commit()
            except Exception as e:
                st.error(f"Error inserting: {e} for row {index}")
                conn.rollback()
                return False
        st.session_state["excel_df"] = df #This way no matter what columns and data is accurate.
        st.success("SQL table created successfully!")
        return True

    except Exception as e:
        st.error(f"Error creating SQL table: {e}")
        conn.rollback()
        return False

def load_sqlite_data(sqlite_file, conn):
    """Loads table names from an uploaded SQLite database."""
    try:
        with sqlite3.connect(sqlite_file.name) as conn_db:
            df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn_db)
        table_names = df['name'].tolist()
        st.success(f"SQLite database loaded. Tables: {', '.join(table_names)}")
        return table_names
    except Exception as e:
        st.error(f"Error loading SQLite database: {e}")
        return None