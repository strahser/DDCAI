import streamlit as st

from PageData.AiChat.chat_logic import process_chat_prompt
from PageData.AiChat.llm import initialize_llm
from PageData.DB.database import execute_sql
from multipage_streamlit import State

def initialize_chat_interface():
    """Initializes chat components."""
    llm = configure_llm_sidebar()
    display_chat_history()

    if prompt := st.chat_input("Your question", key="chat_input"):
        handle_user_prompt(prompt, llm)


def configure_llm_sidebar():
    """Configures LLM settings in sidebar."""
    state = State(__name__)
    llm_choice = st.sidebar.radio("Choose LLM", ["Cloud","Local"])
    if llm_choice == "Cloud":
        cloud_model = st.sidebar.selectbox("Select Cloud Model", ["OpenAI", "Groq", "Anthropic"])
        api_key = st.sidebar.text_input(f"{cloud_model} API Key", type="password",key=state("api_key"))
        return initialize_llm(llm_choice, api_key, cloud_model)
    return initialize_llm(llm_choice)

def display_chat_history():
    """Displays chat message history."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def handle_user_prompt(prompt, llm):
    """Processes user prompt and generates response."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Analyzing..."):
        response = process_chat_prompt(prompt, st.session_state.get("excel_df"), llm)

    with st.chat_message("assistant"):
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


def display_chat_history_sidebar(conn):
    """Displays chat history in sidebar."""
    if st.sidebar.checkbox("Show History"):
        history = execute_sql("SELECT question, answer, timestamp FROM chat_history", conn)
        st.sidebar.dataframe(history)


def chat_with_ai_tab():
    """Handles the Chat with AI tab."""
    st.title("AI Data Analyst Chat")
    initialize_chat_interface()
