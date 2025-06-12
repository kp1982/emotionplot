import streamlit as st

# Initiale Seitensteuerung
if "page" not in st.session_state:
    st.session_state.page = "input"

# Verfügbare Optionen
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
plot_types = ["Interactive Plot", "Wordcloud", "Barplot"]

# Seite 1 – URL-Eingabe
if st.session_state.page == "input":
    st.title("Emotionplot – Schritt 1")
    st.write("Bitte gib die URL ein:")

    url = st.text_input("Enter URL")

    if st.button("Weiter"):
        if url:
            st.session_state.url = url
            st.session_state.page = "plot"
            st.experimental_rerun()
        else:
            st.error("Bitte gib eine gültige URL ein.")

# Seite 2 – Plot-Ausgabe
elif st.session_state.page == "plot":
    st.title("Emotionplot – Schritt 2")
    st.write(f"🔗 URL: {st.session_state.url}")

    # Menü für Plot-Auswahl
    st.subheader("📋 Wähle Plot-Typ")
    selected_plot = st.radio("Plot-Auswahl:", options=plot_types, horizontal=True)

    st.divider()

    # === Interaktiver Plot ===
    if selected_plot == "Interactive Plot":
        st.subheader("📊 Interaktiver Plot")
        
        chunks_interactive = st.number_input(
            "Wie viele Sätze sollen gruppiert werden? (Interaktiver Plot)",
            min_value=1,
            step=1,
            key="chunks_interactive"
        )
        template_interactive = st.selectbox(
            "Wähle ein Plot-Template:",
            options=templates,
            key="template_interactive"
        )

        st.write(f"Template: `{template_interactive}`, Gruppierung: {chunks_interactive}")
        st.write("➡️ Hier könnte ein interaktiver Plot mit Plotly erscheinen.")

    # === Wordcloud ===
    elif selected_plot == "Wordcloud":
        st.subheader("☁️ Wordcloud")

        max_words = st.slider(
            "Anzahl der Wörter in der Wordcloud:",
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

        st.write(f"Max Wörter: {max_words}, Hintergrundfarbe: {background_color}")
        st.write("➡️ Hier könnte eine Wordcloud visualisiert werden.")

    # === Balkendiagramm ===
    elif selected_plot == "Barplot":
        st.subheader("📶 Balkendiagramm")

        chunks_bar = st.number_input(
            "Wie viele Sätze sollen gruppiert werden? (Barplot)",
            min_value=1,
            step=1,
            key="chunks_bar"
        )
        bar_color = st.color_picker("Farbe der Balken:", "#1f77b4", key="bar_color")

        st.write(f"Balkenfarbe: {bar_color}, Gruppierung: {chunks_bar}")
        st.write("➡️ Hier könnte ein Balkendiagramm erscheinen.")

    st.divider()
    if st.button("Zurück"):
        st.session_state.page = "input"
        st.experimental_rerun()
