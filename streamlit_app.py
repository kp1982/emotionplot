import streamlit as st
import json


# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "input"

# Available templates and plot types
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
plot_types = ["Interactive Plot", "Wordcloud", "Barplot"]

# Page 1 – URL or JSON Input
if st.session_state.page == "input":
    st.title("Emotionplot – Step 1")
    st.write("Please enter the URL **or** upload a JSON file:")

    url = st.text_input("Enter URL")
    uploaded_file = st.file_uploader("Or upload a JSON file", type="json")

    file_data = None
    json_error = None

    if uploaded_file is not None:
        try:
            file_data = json.load(uploaded_file)
            st.session_state.file_data = file_data
            st.session_state.url = None  # Clear URL if a file is uploaded
            st.success("JSON file uploaded successfully!")
        except Exception as e:
            json_error = str(e)
            st.error(f"Invalid JSON file: {json_error}")

    if st.button("Next"):
        if uploaded_file and file_data is not None:
            st.session_state.page = "plot"
            st.rerun()
        elif url:
            st.session_state.url = url
            st.session_state.file_data = None  # Clear file data if a URL is entered
            st.session_state.page = "plot"
            st.rerun()
        else:
            st.error("Please enter a valid URL or upload a JSON file.")

    # Display a funny looping GIF
    st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")

# Page 2 – Plot Output
elif st.session_state.page == "plot":
    st.title("Emotionplot – Step 2")
    if st.session_state.get("url"):
        st.write(f"🔗 URL: {st.session_state.url}")
    elif st.session_state.get("file_data") is not None:
        st.write("📄 JSON file uploaded and loaded.")
        # Optionally show part of the JSON:
        with st.expander("Show JSON Preview"):
            st.json(st.session_state.file_data)
    else:
        st.error("No data source found. Please go back and enter a URL or upload a JSON file.")

    # Plot selection menu
    st.subheader("📋 Select Plot Type")
    selected_plot = st.radio("Choose a plot:", options=plot_types, horizontal=True)

    st.divider()

    # === Interactive Plot ===
    if selected_plot == "Interactive Plot":
        st.subheader("📊 Interactive Plot")
        
        chunks_interactive = st.number_input(
            "How many sentences should be grouped? (Interactive Plot)",
            min_value=1,
            step=1,
            key="chunks_interactive"
        )
        template_interactive = st.selectbox(
            "Choose a plot template:",
            options=templates,
            key="template_interactive"
        )

        st.write(f"Template: `{template_interactive}`, Grouping: {chunks_interactive}")
        st.write("➡️ This is where the interactive Plotly chart would appear.")

    # === Wordcloud ===
    elif selected_plot == "Wordcloud":
        st.subheader("☁️ Wordcloud")

        max_words = st.slider(
            "Number of words in the Wordcloud:",
            min_value=10,
            max_value=200,
            value=100,
            step=10,
            key="max_words_wc"
        )
        background_color = st.selectbox(
            "Background color:",
            ["white", "black"],
            key="bg_wc"
        )

        st.write(f"Max words: {max_words}, Background color: {background_color}")
        st.write("➡️ This is where the word cloud would be displayed.")

    # === Barplot ===
    elif selected_plot == "Barplot":
        st.subheader("📶 Barplot")

        chunks_bar = st.number_input(
            "How many sentences should be grouped? (Barplot)",
            min_value=1,
            step=1,
            key="chunks_bar"
        )

        st.write(f"Grouping: {chunks_bar}")
        st.write("➡️ This is where the bar plot would appear.")

    st.divider()

    if st.button("Back"):
        st.session_state.page = "input"
        st.rerun()
