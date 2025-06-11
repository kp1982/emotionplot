import streamlit as st
import tkinter as tk

st.title("Emotionplot")
st.write(
    "Instructions for user."
)

import streamlit as st

st.title("Emotionplot")
st.write("Instructions for user.")

# Define available templates
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]

# Create a form for user input
with st.form("User input"):
    url = st.text_input("Enter URL")
    chunks = st.number_input("How many sentences would you like to group for plotting?", min_value=1, step=1)
    template = st.selectbox("Choose a plotting template:", options=templates)  
    
    submitted = st.form_submit_button("Submit")

# If form is submitted, ensure inputs are valid
if submitted:
    if url and chunks:
        input_data = {
            "url": url,
            "chunks": chunks,
            "template": template
        }
        st.write("Your input:", input_data)
    else:
        st.error("Please provide both a valid URL and a numerical value.")


#api_url = ""
#response = requests.post(api_url, json=ride_data)

#if response.status_code == 200:
#    prediction_data = response.json()
#    emotion_prediction = prediction_data.get("prediction", "Not available")
#    st.success(f"Predicted Emotions: {prediction_data}")
#else:
#    st.error(f"Error: {response.status_code}")



