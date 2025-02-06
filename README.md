# DDCAI - Streamlit Data Analysis and AI Chat Application

This Streamlit application provides a comprehensive data analysis and AI chat platform. It allows users to upload data, interact with AI-powered assistants, execute SQL and Python code, and manage data through an admin panel.

## Features

*   **Data Upload:** Upload data from Excel and SQLite databases.
*   **AI Chat:** Interact with AI assistants powered by OpenAI, Groq, or Anthropic.
*   **Code Execution:** Execute SQL and Python code snippets directly within the app.
*   **Data Analysis:** Analyze data using SQL queries, Python scripts, and Matplotlib visualizations.
*   **Admin Panel:** Manage API keys and code snippets through a dedicated admin interface.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd DDCAI
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   **On Windows:**

        ```bash
        venv\Scripts\activate
        ```

    *   **On macOS and Linux:**

        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install streamlit pandas openpyxl openai groq anthropic multipage-streamlit
    pip install pandasai
    ```

## Usage

1.  **Run the main application:**

    ```bash
    streamlit run app.py
    ```

    This will start the Streamlit application in your web browser.


    This will start the admin panel in a separate Streamlit application in your web browser.

## Application Structure

*   **`app.py`:** The main Streamlit application file.
*   **`streamlit_admin.py`:** The Streamlit application file for the admin panel.
*   **`streamlit_app/`:** Contains the application logic and UI components.

    *   **`database.py`:** Handles database initialization, queries, and updates.
    *   **`data_loader.py`:** Loads data from Excel and SQLite files.
    *   **`llm.py`:** Manages AI model initialization and interaction.
    *   **`chat_logic.py`:** Processes user prompts and generates AI responses.
    *   **`utils.py`:** Contains helper functions for code execution and variable management.
    *   **`tabs.py`:** Defines the layout and functionality of each tab in the application.
    *   **`admin_panel.py`:** Defines the layout and functionality of the admin panel.

## Configuration

*   **API Keys:** API keys for OpenAI, Groq, and Anthropic can be added and managed through the admin panel or directly in the `api_keys` table.
*Make sure you have all the dependencies set up and ready to run!

## Dependencies

*   **`streamlit`:** A Python library for building web applications.
*   **`pandas`:** A data analysis and manipulation library.
*   **`openpyxl`:** A Python library for reading and writing Excel files.
*   **`openai`:** The OpenAI Python library for accessing OpenAI models.
*   **`groq`:** The Groq Python library for accessing Groq models.
*   **`anthropic`:** The Anthropic Python library for accessing Anthropic models.

## Contributing

Contributions are welcome! Please submit pull requests with detailed descriptions of the changes.