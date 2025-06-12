import streamlit as st

# Define available templates
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]

# Simulate page navigation using session state
if "page" not in st.session_state:
    st.session_state.page = "input"

# Page Navigation Controls
if st.session_state.page == "input":
    st.title("Emotionplot - Step 1")
    st.write("Enter the URL to begin.")

    url = st.text_input("Enter URL")

    if st.button("Next"):
        if url:
            st.session_state.url = url
            st.session_state.page = "plot"
            st.experimental_rerun()
        else:
            st.error("Please enter a valid URL.")

elif st.session_state.page == "plot":
    st.title("Emotionplot - Step 2")

    st.write(f"URL provided: {st.session_state.url}")

    chunks = st.number_input("How many sentences would you like to group for plotting?", min_value=1, step=1, value=5)
    template = st.selectbox("Choose a plotting template:", options=templates)

    if st.button("Plot"):
        st.write("🔧 Placeholder for plot rendering here...")
        st.write(f"Using template: `{template}` with chunks = {chunks}")
        # You would call your plotting function here

    if st.button("Back"):
        st.session_state.page = "input"
        st.experimental_rerun()
