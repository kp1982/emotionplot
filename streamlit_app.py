import streamlit as st


st.title("Emotionplot!!!!!")
st.write("Instructions for user.")

# Define available templates
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]

# Create a form for user input
with st.form("User input"):
    url = st.text_input("Enter URL")
    submitted = st.form_submit_button("Submit")

# If form is submitted, ensure inputs are valid
if submitted:
    if url and chunks:
        input_data = {
            "url": url,
        }
        st.write("Your input:", input_data)
    else:
        st.error("Please provide both a valid URL and a numerical value.")



