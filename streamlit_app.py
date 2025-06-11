import streamlit as st
import tkinter as tk

st.title("Emotionplot")
st.write(
    "Instructions for user."
)

# Define available templates
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]

# Create a form for user input
with st.form("User input"):
    url = st.text_input("Enter URL")
    chunks = st.number_input("How many sentences would you like to group for plotting?", min_value=1, step=1)
    template = st.selectbox("Choose a plotting template:", options=templates)  # Dropdown menu for template selection
    
    submitted = st.form_submit_button("Submit")

# If form is submitted, create a dictionary with the input data
if submitted:
    input_data = {
        "url": url,
        "chunks": chunks,
        "template": template  # Store selected template
    }

    st.write("Your input:", input_data)

#api_url = ""
#response = requests.post(api_url, json=ride_data)

#if response.status_code == 200:
#    prediction_data = response.json()
#    emotion_prediction = prediction_data.get("prediction", "Not available")
#    st.success(f"Predicted Emotions: {prediction_data}")
#else:
#    st.error(f"Error: {response.status_code}")



