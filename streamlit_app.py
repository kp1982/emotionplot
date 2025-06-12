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

    # Plot-Konfiguration (zentral für alle Plottypen)
    st.subheader("🛠️ Plot-Konfiguration")
    chunks = st.number_input("Wie viele Sätze sollen gruppiert werden?", min_value=1, step=1, value=5)
    template = st.selectbox("Wähle ein Plot-Template:", options=templates)

    # Menü für Plot-Auswahl
    st.subheader("📋 Wähle Plot-Typ")
    selected_plot = st.radio("Plot-Auswahl:", options=plot_types, horizontal=True)

    st.divider()

    # Dynamische Plotanzeige je nach Auswahl
    if selected_plot == "Interactive Plot":
        st.subheader("📊 Interaktiver Plot")
        st.write(f"Template: `{template}`, Gruppierung: {chunks}")
        st.write("➡️ Hier könnte ein interaktiver Plot mit Plotly erscheinen.")

    elif selected_plot == "Wordcloud":
        st.subheader("☁️ Wordcloud")
        st.write("➡️ Hier könnte eine Wordcloud visualisiert werden.")

    elif selected_plot == "Barplot":
        st.subheader("📶 Balkendiagramm")
        st.write(f"Gruppierung: {chunks}")
        st.write("➡️ Hier könnte ein Balkendiagramm erscheinen.")

    st.divider()

    if st.button("Zurück"):
        st.session_state.page = "input"
        st.experimental_rerun()
