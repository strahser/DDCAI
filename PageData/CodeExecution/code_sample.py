# 1. Area Distribution
import streamlit as st

from matplotlib import pyplot as plt


def area_distribution(df):
    """
    Displays a histogram of the area distribution of elements.

    Args:
        df (pd.DataFrame): DataFrame containing the 'Area' column.
    """

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['Area'].dropna(), bins=30, color='green', edgecolor='black', alpha=0.7)
    ax.set_title('Area Distribution of Elements')
    ax.set_xlabel('Area (sq. m)')
    ax.set_ylabel('Number of Elements')
    ax.grid(True)

    st.pyplot(fig)
    st.write(f"""
    **Analysis:**
    - Average Area: {df['Area'].mean():.2f} sq. m
    - Maximum Area: {df['Area'].max():.2f} sq. m
    - 75% of elements have an area less than {df['Area'].quantile(0.75):.2f} sq. m
    """)


# 2. Top Families by Element Count
def family_name_distribution(df):
    """
    Displays a bar chart of the top 10 families by the number of elements.

    Args:
        df (pd.DataFrame): DataFrame containing the 'Family Name' column.
    """

    top_families = df['Family Name'].value_counts().head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    top_families.plot(kind='bar', ax=ax, color='purple')
    ax.set_title('Top 10 Families by Number of Elements')
    ax.set_xlabel('Family')
    ax.set_ylabel('Number of Elements')
    ax.tick_params(axis='x', rotation=45)

    st.pyplot(fig)
    st.write(f"""
    **Observation:**
    - Most common family: '{top_families.index[0]}' ({top_families.iloc[0]} elements)
    - Top 3 families represent {top_families.head(3).sum() / len(df) * 100:.1f}% of the total number of elements
    """)


# 3. Comparison of Average Quantity by Family
def family_quantity_comparison(df):
    """
    Displays a bar chart of the average quantity of elements per family (Top 10).

    Args:
        df (pd.DataFrame): DataFrame containing the 'Family Name' and 'Quantity' columns.
    """

    family_avg = df.groupby('Family Name')['Quantity'].mean().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    family_avg.plot(kind='bar', ax=ax, color='orange')
    ax.set_title('Average Number of Elements by Family (Top 10)')
    ax.set_xlabel('Family')
    ax.set_ylabel('Average Quantity')
    ax.tick_params(axis='x', rotation=45)

    st.pyplot(fig)
    st.write(f"""
    **Findings:**
    - Family '{family_avg.index[0]}' has the highest average quantity: {family_avg.iloc[0]:.1f}
    - Difference between the first and second place: {family_avg.iloc[0] - family_avg.iloc[1]:.1f}
    """)


# 4. Scatter Plot: Area vs. Quantity
def area_vs_quantity(df):
    """
    Displays a scatter plot showing the relationship between Area and Quantity.

    Args:
        df (pd.DataFrame): DataFrame containing the 'Area' and 'Quantity' columns.
    """

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['Quantity'], df['Area'], alpha=0.6, color='red', edgecolors='w')
    ax.set_title('Relationship between Area and Quantity of Elements')
    ax.set_xlabel('Quantity')
    ax.set_ylabel('Area (sq. m)')
    ax.grid(True)

    st.pyplot(fig)
    st.write("""
    **Correlation:**
    - Elements with a quantity greater than ______ typically have an area in the range of ______
    - There is a ______ relationship observed between the quantity and area of elements
    """)


# 5. Box Plot of Area Distribution by Family
def family_area_distribution(df):
    """
    Displays a box plot of the area distribution for the top families.

    Args:
        df (pd.DataFrame): DataFrame containing the 'Family Name' and 'Area' columns.
    """

    top_families = df['Family Name'].value_counts().head(5).index
    filtered_df = df[df['Family Name'].isin(top_families)]

    fig, ax = plt.subplots(figsize=(12, 6))
    filtered_df.boxplot(column='Area', by='Family Name', ax=ax)
    ax.set_title('Area Distribution by Top Families')
    ax.set_xlabel('Family')
    ax.set_ylabel('Area (sq. m)')
    ax.tick_params(axis='x', rotation=45)
    plt.suptitle('')  # Remove default title

    st.pyplot(fig)
    st.write("""
    **Analysis:**
    - The ______ family has the largest range of area values.
    - The median area for ______ is ______ sq. m.
    """)


df = st.session_state["excel_df"]

with st.expander("Area Distribution"):
    area_distribution(df)

with st.expander("Distribution by Families"):
    family_name_distribution(df)

with st.expander("Quantity Comparison"):
    family_quantity_comparison(df)

with st.expander("Scatter Plot: Area vs. Quantity"):
    area_vs_quantity(df)

with st.expander("Box Plot of Area Distribution by Family"):
    family_area_distribution(df)