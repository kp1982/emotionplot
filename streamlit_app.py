import streamlit as st
import pandas as pd
import json
import io
import ast

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "input"

# Available templates and plot types
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
plot_types = ["Interactive Plot", "Wordcloud", "Barplot"]

# Page 1 – URL Input
#if st.session_state.page == "input":
 #   st.title("Emotionplot – Step 1")
  #  st.write("Please enter the URL:")

   # url = st.text_input("Enter URL")

    #if st.button("Next"):
     #   if url:
      #      st.session_state.url = url
       #     st.session_state.page = "plot"
        #    st.experimental_rerun()
        #else:
         #   st.error("Please enter a valid URL.")

# JSON-Datei laden
if uploaded_file:
    try:
        # Versuche normales JSON zu laden
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        raw_data = json.load(stringio)
    except json.JSONDecodeError:
        try:
            # Fallback: Versuche, mit ast.literal_eval zu parsen
            raw_text = uploaded_file.getvalue().decode("utf-8")
            raw_data = ast.literal_eval(raw_text)
            st.warning("⚠️ Die Datei war kein gültiges JSON – wurde automatisch konvertiert.")
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der Datei: {str(e)}")
            st.stop()

    # Überprüfe Struktur
    if "emotions" in raw_data:
        df = pd.DataFrame(raw_data["emotions"])
        st.session_state.data = df
        st.session_state.page = "plot"
        st.experimental_rerun()
    else:
        st.error("❌ Die Datei enthält keinen 'emotions'-Schlüssel.")



    #st.divider()
    #st.markdown("#### 🐵 While you're waiting, enjoy this GIF:")
    
    # Display a funny looping GIF
    st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")


# Page 2 – Plot Output
elif st.session_state.page == "plot":
    st.title("Emotionplot – Step 2")
 #   st.write(f"🔗 URL: {st.session_state.url}")
    st.write("✅ JSON-Datei erfolgreich geladen!")

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
        st.experimental_rerun()
    if st.button("Back"):
        st.session_state.page = "input"
        st.experimental_rerun()
