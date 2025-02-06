from pandasai import SmartDataframe
import matplotlib.pyplot as plt
import streamlit as st

def process_chat_prompt(prompt: str, df, llm):
    """Processes the user's chat prompt using LLM."""
    response = ""
    try:
        if df is not None and llm is not None:
            sdf = SmartDataframe(df, config={"llm": llm})
            response = sdf.chat(prompt)

            if "plot" in prompt.lower():
                plt.figure()
                df.plot()
                st.pyplot(plt)
        else:
            response = "Please upload data and configure the LLM."
    except Exception as e:
        response = f"Error: {str(e)}"
    return response