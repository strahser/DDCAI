from pandasai.llm.local_llm import LocalLLM
from pandasai.llm import  OpenAI
from groq import Groq
from anthropic import Anthropic
import streamlit as st

def initialize_llm(llm_choice: str, api_key: str = None, cloud_model: str = "OpenAI"):
    """Initializes the Language Model based on user choice."""
    if llm_choice == "Local":
        return LocalLLM(api_base="http://localhost:11434/v1", model="llama3")
    elif llm_choice == "Cloud":
        if api_key:
            if cloud_model == "OpenAI":
                return OpenAI(api_token=api_key)
            elif cloud_model == "Groq":
                return Groq(api_key=api_key)
            elif cloud_model == "Anthropic":
                return Anthropic(api_key=api_key)
            else:
                st.error("Invalid cloud model selected.")
                return None
        else:
            st.warning("Enter API key for Cloud Mode.")
            return None
    else:
        return None