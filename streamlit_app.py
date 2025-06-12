import streamlit as st
import pandas as pd
import json

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "input"

templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
plot_types = ["Interactive Plot", "Wordcloud", "Barplot"]

# Seite 1 – Datei-Uploader
if st.session_state.page == "input":
    st.title("Emotionplot – Step 1")
    st.write("Bitte lade deine JSON-Datei hoch:")

    file = st.file_uploader("JSON-Datei auswählen", type=["json"])
    if file is not None:
        data = json.load(file)
        st.session_state.data = data
        st.session_state.page = "plot"
        st.experimental_rerun()

    st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")

# Seite 2 – Plot-Auswahl und Anzeige
elif st.session_state.page == "plot":
    st.title("Emotionplot – Step 2")

    data = st.session_state.data
    # Passe diesen Key ggf. an, falls deine Struktur anders ist!
    if "emotions" in data:
        df = pd.DataFrame(data["emotions"])
    else:
        df = pd.DataFrame(data)

    st.dataframe(df.head())

    st.subheader("📋 Plot Typ auswählen")
    selected_plot = st.radio("Plot wählen:", options=plot_types, horizontal=True)
    st.divider()

    if selected_plot == "Interactive Plot":
        st.subheader("📊 Interactive Plot")
        chunks_interactive = st.number_input(
            "Wie viele Sätze sollen gruppiert werden? (Interactive Plot)",
            min_value=1,
            step=1,
            key="chunks_interactive"
        )
        template_interactive = st.selectbox(
            "Plot-Template wählen:",
            options=templates,
            key="template_interactive"
        )
        st.write(f"Template: {template_interactive}, Gruppierung: {chunks_interactive}")
        st.write("➡️ Hier würde der Interactive Plot erscheinen.")

    elif selected_plot == "Wordcloud":
        st.subheader("☁️ Wordcloud")
        max_words = st.slider(
            "Wörteranzahl in der Wordcloud:",
            min_value=10,
            max_value=200,
            value=100,
            step=10,
            key="max_words_wc"
        )
        background_color = st.selectbox(
            "Hintergrundfarbe:",
            ["white", "black"],
            key="bg_wc"
        )
        st.write(f"Max Wörter: {max_words}, Hintergrund: {background_color}")
        st.write("➡️ Hier würde die Wordcloud erscheinen.")

    elif selected_plot == "Barplot":
        st.subheader("📶 Barplot")
        chunks_bar = st.number_input(
            "Wie viele Sätze sollen gruppiert werden? (Barplot)",
            min_value=1,
            step=1,
            key="chunks_bar"
        )
        st.write(f"Gruppierung: {chunks_bar}")
        st.write("➡️ Hier würde der Barplot erscheinen.")

    st.divider()
    if st.button("Zurück"):
        st.session_state.page = "input"
        st.experimental_rerun()
