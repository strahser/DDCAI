import streamlit as st

from matplotlib import pyplot as plt
import seaborn as sns

""""
we have a pandas data frame with the following columns Category,Family Name,Area,
make a function in python that will use st.write to display data. We are making snippets of the code to be displayed
in streamlit.create 
# 1. Area Distribution 
# 2. Top Families by Element Count
# 3. Comparison of Average Quantity by Family
# 4. Scatter Plot: Area vs. Quantity 
# 5. Box Plot of Area Distribution by Family
use matplotlib as plt seaborn as sns
crate tables and charts
"""


# 1. Area Distribution

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


def display_data_insights(df):
    """
    Displays data insights from the DataFrame using Streamlit.

    Args:
        df (pd.DataFrame): The input DataFrame with columns 'Category', 'Family Name', 'Area', and 'Quantity'.
    """

    st.header("Data Insights")

    # 1. Area Distribution
    st.subheader("1. Area Distribution")
    st.write("Distribution of areas.  This shows the range and common values of the Area variable.")

    fig_area, ax_area = plt.subplots(figsize=(8, 5))  # Create figure and axes explicitly
    sns.histplot(df['Area'], ax=ax_area, kde=True)  # Pass the axes to seaborn
    ax_area.set_title("Area Distribution")
    st.pyplot(fig_area)  # Use st.pyplot to display the figure

    # 2. Top Families by Element Count
    st.subheader("2. Top Families by Element Count")
    st.write("Shows the top families based on the number of items they have in the dataset.")

    family_counts = df['Family Name'].value_counts().sort_values(ascending=False)
    top_families = family_counts.head(10)

    fig_families, ax_families = plt.subplots(figsize=(10, 6))
    top_families.plot(kind='bar', ax=ax_families)
    ax_families.set_title("Top 10 Families by Element Count")
    ax_families.set_xlabel("Family Name")
    ax_families.set_ylabel("Count")
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
    st.pyplot(fig_families)

    family_counts_df = pd.DataFrame({'Family Name': family_counts.index, 'Count': family_counts.values})
    st.write("Top Families Count Table:")
    st.dataframe(family_counts_df.head(10), height=300)

    # 3. Comparison of Average Quantity by Family
    st.subheader("3. Comparison of Average Quantity by Family")
    st.write(
        "Shows the average quantity for each family.  This helps identify families with higher average quantities.")

    avg_quantity_by_family = df.groupby('Family Name')['Quantity'].mean().sort_values(ascending=False)
    top_avg_quantities = avg_quantity_by_family.head(10)

    fig_quantity, ax_quantity = plt.subplots(figsize=(10, 6))
    top_avg_quantities.plot(kind='bar', ax=ax_quantity)
    ax_quantity.set_title("Top 10 Families by Average Quantity")
    ax_quantity.set_xlabel("Family Name")
    ax_quantity.set_ylabel("Average Quantity")
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
    st.pyplot(fig_quantity)

    avg_quantity_df = pd.DataFrame(
        {'Family Name': avg_quantity_by_family.index, 'Average Quantity': avg_quantity_by_family.values})
    st.write("Average Quantity by Family Table:")
    st.dataframe(avg_quantity_df.head(10), height=300)

    # 4. Scatter Plot: Area vs. Quantity
    st.subheader("4. Scatter Plot: Area vs. Quantity")
    st.write("Visualizes the relationship between area and quantity.  Helps identify any correlations or patterns.")

    fig_scatter, ax_scatter = plt.subplots(figsize=(8, 6))
    sns.scatterplot(x='Area', y='Quantity', data=df, ax=ax_scatter)
    ax_scatter.set_title("Area vs. Quantity")
    st.pyplot(fig_scatter)

    # 5. Box Plot of Area Distribution by Family
    st.subheader("5. Box Plot of Area Distribution by Family")
    st.write(
        "Compares the area distribution for different families.  Shows the spread and central tendency of the area "
        "for each family.")

    top_families_list = top_families.index.tolist()
    filtered_df = df[df['Family Name'].isin(top_families_list)]

    fig_boxplot, ax_boxplot = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='Family Name', y='Area', data=filtered_df, ax=ax_boxplot)
    ax_boxplot.set_title("Area Distribution by Top 10 Family")
    ax_boxplot.set_xlabel("Family Name")
    ax_boxplot.set_ylabel("Area")
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
    plt.tight_layout()
    st.pyplot(fig_boxplot)
