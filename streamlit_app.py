import streamlit as st
import json
import plotly.graph_objects as go
import pandas as pd
import requests

from emotion_frequency import plot_emotion_frequency
from emotion_over_time import plot_emotion_evolution
from utils import extract_book_id, get_book_metadata, get_cover_url

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from collections import Counter
import time
import plotly.colors
from stacked_bar_plot import plot_stacked_emotions
from poem_stacked_bar_plot import poem_plot_stacked_emotions
from poem_emotion_over_time import poem_plot_emotion_evolution

import textblob
from textblob import download_corpora

from nrclex import NRCLex
import re
from utils import text_to_latex, latex_to_paragraph_dataframe, get_emotion


import corpora

import nltk

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("wordnet")

# Download TextBlob corpora
try:
    download_corpora.download_all()
except:
    pass

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "start"
if "input_type" not in st.session_state:
    st.session_state.input_type = None



# Available templates and plot types
plot_types = ["Interactive Plot", "Wordcloud", "Barplot", "Curve", "Emotion Examples"]
friendly_plot_labels = {
    "Interactive Plot": "📊 Emotion Overview (Stacked)",
    "Wordcloud": "☁️ Wordcloud of Emotional Words",
    "Barplot": "📶 Average Emotion Intensity",
    "Curve": "📈 Emotional Flow Over Time",
    "Emotion Examples": "🔍 Example Lines by Emotion"
}
plot_options_display = list(friendly_plot_labels.values())

st.markdown("""
<style>
/* Fix uneven alignment of radio options in horizontal layout */
section[data-testid="stRadio"] label {
    white-space: nowrap;
    padding-right: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# Page 0 – Selection of text type
if st.session_state.page == "start":
    st.title("📚 Welcome to Emotionplot")
    st.write("Explore the emotional dynamics of literary texts. Select whether you want to analyze a poem or a novel to get started.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 My input is a novel"):
            st.session_state.input_type = "novel"
            st.session_state.page = "novel_input"
            st.rerun()
    with col2:
        if st.button("📝 My input is a poem"):
            st.session_state.input_type = "poem"
            st.session_state.page = "poem_input"
            st.rerun()



# --- INIT SESSION STATE ---
if "page" not in st.session_state:
    st.session_state.page = "input"
if "confirm_clicked" not in st.session_state:
    st.session_state.confirm_clicked = False

# --- PAGE: Novel Input ---
if st.session_state.page == "novel_input":
    st.title("📖 Step 1: Paste Your Novel Link")


    # === CASE 1: Before confirmation ===
    if not st.session_state.confirm_clicked:
        st.write("Paste a URL from **Project Gutenberg** or another online source. We'll fetch the text and analyze its emotions.")
        url = st.text_input("Enter the URL of the novel/text:")
        st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")

        if st.button("Confirm"):
            if url.strip():
                st.session_state.confirm_clicked = True
                st.session_state.url = url.strip()
                st.rerun()
            else:
                st.error("Please enter a valid URL.")

    # === CASE 2: Spinner while fetching ===
    elif "file_data" not in st.session_state:

        with st.spinner("🔄 Analyzing text and extracting emotions..."):
            try:
                response = requests.get(
                    "https://emotionplot-api-znpzhhue6a-ew.a.run.app/analyze",
                    params={
                        "url": st.session_state.url,
                        "sentences_per_chunk": 5,
                        "model": "accurate",
                    },
                    timeout=900,
                )
                response.raise_for_status()
                data = response.json()
                st.session_state.file_data = data
                #st.success("✅ Done analyzing your novel!")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ API request failed: {e}")
                st.session_state.confirm_clicked = False
                st.stop()
        st.rerun()

    # === CASE 3: After success ===
    elif "file_data" in st.session_state:
        st.success("✅ Done analyzing your novel!")

        try:
            url = st.session_state.url
            book_id = url.strip("/").split("/")[-1]
            meta_url = f"https://gutendex.com/books/{book_id}"
            meta_response = requests.get(meta_url)
            meta_response.raise_for_status()
            metadata = meta_response.json()
            title = metadata.get("title", "Unknown Title")
            authors = metadata.get("authors", [])
            author = authors[0]["name"] if authors else "Unknown Author"
            cover_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"

            info_col, cover_col = st.columns([2, 1])
            with info_col:
                st.write(f"📖 {title}")
                st.write(f"✍️ {author}")
            with cover_col:
                st.image(cover_url, width=150)

        except Exception:
            st.write("📖 Unknown Title")
            st.write("✍️ Unknown Author")

        # Navigation buttons
        if st.button("🚀 Go to plots"):
            st.session_state.page = "plot_novel"
            st.rerun()

        if st.button("📚 Get Similar Books"):
            st.session_state.page = "recommend_books"
            st.session_state.recommend_clicked = True
            st.rerun()

        if st.button("📖 Submit Another Novel"):
            for key in ["file_data", "url", "confirm_clicked"]:
                st.session_state.pop(key, None)
            st.session_state.page = "novel_input"
            st.rerun()

        if st.button("📝 Submit a Poem Instead"):
            st.session_state.clear()
            st.session_state.page = "poem_input"
            st.session_state.input_type = "poem"
            st.rerun()

# Fetch recommendations if requested
if st.session_state.get("recommend_clicked") and "recommendations" not in st.session_state:
    with st.spinner("🔎 Finding similar books..."):
        try:
            response = requests.post(
                "https://emotionplot-api-znpzhhue6a-ew.a.run.app/recommend",
                json=st.session_state.file_data,
                timeout=60
            )
            response.raise_for_status()
            rec_data = response.json()
            st.session_state.recommendations = rec_data
            st.success("✅ Recommendations loaded!")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to get recommendations: {e}")
    # Prevent re-fetching on every rerun
    st.session_state.recommend_clicked = False



# === Page 2: Poem Input ===
if st.session_state.page == "poem_input":
    st.title("📝 Step 1: Submit your poem")

    # === CASE 1: Before confirmation ===
    if not st.session_state.get("confirm_clicked"):
        st.markdown("""
        Paste your poem below to begin the emotional analysis.
        This works best for shorter, expressive texts.

        💡 *Tip: Free verse, spoken word, or lyrical stanzas all work great!*
        """)

        # Poem input
        poem_text = st.text_area(
            "Enter your poem here:",
            height=300,
            key="poem_text_input"
        )

        # Fun GIF
        # st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")

        if st.button("Confirm"):
            if poem_text.strip():
                st.session_state.poem_text = poem_text
                st.session_state.confirm_clicked = True
                st.session_state.poem_latex = text_to_latex(poem_text)
                st.session_state.paragraph_df = latex_to_paragraph_dataframe(st.session_state.poem_latex)
                st.rerun()
            else:
                st.error("❌ Please paste your poem before continuing.")

    # === CASE 2: Spinner while fetching ===
    elif (
        st.session_state.get("confirm_clicked")
        and "poem_emotion_data" not in st.session_state
        and "emotion_analysis_failed" not in st.session_state
    ):
        with st.spinner("🔄 Analyzing emotions in your poem..."):
            try:
                response = requests.get(
                    "https://emotionplot-api-644268373090.europe-west1.run.app/analyze_poemlines/",
                    params={"poem_text": st.session_state.poem_latex, "model": "accurate"},
                    timeout=1800
                )
                response.raise_for_status()
                st.session_state.poem_emotion_data = response.json()
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Emotion analysis failed: {e}")
                st.session_state.confirm_clicked = False
                st.session_state.emotion_analysis_failed = True
                st.stop()
        st.rerun()

    # === CASE 3: After success ===
    elif st.session_state.get("poem_emotion_data"):
        st.success("✅ Done analyzing your poem!")

        st.markdown("""
            <div style="margin-bottom: 0.25rem; font-size: 1.2rem;">
            📄 <strong>Your Submitted Poem:</strong>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("""
            <style>
            .scrollable-code {
                max-height: 300px;
                overflow-y: auto;
                background-color: #0e1117;
                padding: 1rem;
                border-radius: 0.5rem;
                font-family: monospace;
                white-space: pre-wrap;
            }
            </style>
        """, unsafe_allow_html=True)

        poem_html = st.session_state.get("poem_text", "").replace("\n", "<br>")
        st.markdown(f'<div class="scrollable-code">{poem_html}</div>', unsafe_allow_html=True)


        st.markdown("<div style='margin-top: 1.5rem'></div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

        #st.button("📊 Go to Plot", key="go_to_plot")

        #st.button("📝 Submit a New Poem", key="submit_new_poem")

        # Button actions
        if st.button("📊 Go to Plot"):
            st.session_state.page = "plot_poem"
            st.rerun()

        if st.button("📝 Submit a New Poem"):
            for key in [
                "confirm_clicked", "poem_latex", "paragraph_df",
                "poem_emotion_data", "poem_text", "emotion_analysis_failed"
            ]:
                st.session_state.pop(key, None)
            st.rerun()

        if st.button("📖 Submit a Novel"):
            st.session_state.clear()
            st.session_state.page = "novel_input"
            st.session_state.input_type = "novel"
            st.rerun()


#################################################
# Page 3 – Plot Output Novel
#################################################
elif st.session_state.page == "plot_novel":
    st.title("📖 Step 2: Explore the Emotions of the Novel")
    # st.write("Choose a visualization below to see how emotions unfold in your text.")

    if st.session_state.get("file_data") is None:
        st.error("No data source found. Please go back and enter a URL.")
        st.stop()


    novel_data = st.session_state.file_data  #Load saved data from session state

    if st.session_state.get("url"):
        url = st.session_state.url
        # Only fetch Gutenberg metadata if URL is from gutenberg.org
        if "gutenberg.org" in url:
            try:
                book_id = url.strip("/").split("/")[-1]
                meta_url = f"https://gutendex.com/books/{book_id}"
                response = requests.get(meta_url)
                response.raise_for_status()
                metadata = response.json()
                book_title = metadata.get("title", "Unknown Title")
                authors = metadata.get("authors", [])
                author_name = authors[0]["name"] if authors else "Unknown Author"
                #cover_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"

                info_col, cover_col = st.columns([2, 1])
                with info_col:
                    st.write(f"📖 {book_title}")
                    st.write(f"✍️ {author_name}")
                #with cover_col:
                #    cover_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"
                #    st.image(cover_url, width=150)
            except Exception:
                st.write("📖 Unknown Title")
                st.write("✍️ Unknown Author")


    # Plot selection menu
    st.subheader("📋 Select Output Type")
    selected_friendly_name = st.radio(
        "📋 Select a visualization",
        options=plot_options_display,
        #horizontal=True,
        key="novel_plot_selector"
    )
    selected_plot = next(
        (k for k, v in friendly_plot_labels.items() if v == selected_friendly_name),
        None
    )
    if selected_plot is None:
        st.error("⚠️ Could not match selected plot option.")
        st.stop()

    st.divider()

    # === Interactive Plot ===

    # Available templates and plot types
    templates = ["plotly_dark",  "simple_white"] #"plotly_white",

    # Add this list of color scales (Plotly built-ins)
    color_scales = [
        "Plotly", "Viridis", "Plasma", "Inferno", "Jet", "Rainbow", "RdBu","Portland"
    ]


    if selected_plot == "Interactive Plot":
        st.subheader(friendly_plot_labels.get(selected_plot, selected_plot))

        with st.sidebar:
            st.subheader("🔧 Settings Menu")
            chunks_interactive = st.number_input(
                "How many groups sentences do you want to be displayed?",
                min_value=1,
                max_value=100,
                value=10,
                step=1,
                key="chunks_interactive"
            )

            # Only color scale selection remains
            color_scale_options = {
                "Vibrant": "Plotly",
                "Cool": "Viridis",
                "Warm": "Plasma",
                "Dark": "Inferno",
                "Classic": "Jet",
                "Rainbow": "Rainbow",
                "Red-Blue": "RdBu",
                "Portland": "Portland"
            }
            color_scale_label = st.selectbox(
                "Choose a color scale:",
                options=list(color_scale_options.keys()),
                key="color_scale_interactive"
            )
            color_scale_interactive = color_scale_options[color_scale_label]

            st.subheader("Want to get book recommendations?")
            if st.button("📚 Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True
                st.rerun()

            st.subheader("Ready to explore another text?")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()

        try:
            df1 = pd.DataFrame(novel_data)
            df_other_model = pd.DataFrame.from_records(df1["emotions"].to_list())
            emotions_df = df_other_model["Top_3_Emotions"].apply(pd.Series).fillna(0)
            emotions_df["chunk"] = emotions_df.index
            plot_stacked_emotions(
                emotions_df,
                group_size=chunks_interactive,
                color_scale=color_scale_interactive
            )
        except Exception as e:
            st.error(f"Error while plotting: {e}")

        # === Navigation Buttons (all stacked) ===
        st.markdown("---")
        if st.button("📚 Get Similar Books"):
            st.session_state.page = "recommend_books"
            st.session_state.recommend_clicked = True
            st.rerun()

        if st.button("📖 Enter Another Novel"):
            st.session_state.clear()
            st.session_state.page = "novel_input"
            st.session_state.input_type = "novel"
            st.rerun()

        if st.button("📝 Submit a Poem"):
            st.session_state.clear()
            st.session_state.page = "poem_input"
            st.session_state.input_type = "poem"
            st.rerun()


    # === Wordcloud ===
    elif selected_plot == "Wordcloud":
        st.subheader(friendly_plot_labels.get(selected_plot, selected_plot))

        with st.sidebar:
            st.subheader("🔧 Settings Menu")
            background_color = st.selectbox(
            "Background color:",
            ["white", "black"],
            key="bg_wc"
            )


        if st.session_state.get("file_data") is not None:
            try:
                # Step 1: Extract the list of emotion entries
                emotions_list = novel_data.get("emotions", [])

                # :mag: Get list of all unique dominant emotions
                available_emotions = sorted(set(entry.get("Predicted_Emotion", "unknown") for entry in emotions_list))

                # Define target emotions
                target_emotions = {'anger', 'fear', 'surprise', 'sadness', 'joy', 'disgust'}


                filtered_emotions = [entry for entry in emotions_list if entry.get("Predicted_Emotion") in target_emotions]
                available_emotions2 = sorted(set(entry.get("Predicted_Emotion", "unknown") for entry in filtered_emotions))

                # Select emotion to filter by
                with st.sidebar:
                    selected_emotion = st.selectbox("Filter wordcloud by dominant emotion:", ["All"] + available_emotions2)

                # Step 2: Filter entriess
                if selected_emotion != "All":
                    emotions_list = [entry for entry in emotions_list if entry.get("Predicted_Emotion") == selected_emotion]

                # Step 3: Combine all 'chunk' texts into one string
                all_text = " ".join(entry.get("chunk", "") for entry in emotions_list)

                # Step 4: Tokenize and count word frequencies
                stopwords =  ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as",
                              "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot",
                              "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each",
                              "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd",
                              "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
                              "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me",
                              "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
                              "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
                              "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
                              "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
                              "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
                              "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while",
                              "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
                              "you're", "you've", "your", "yours", "yourself", "yourselves"]

                words = re.findall(r"\b[a-z]{3,}\b", all_text.lower())

                # Use NRCLex to determine emotional words
                emotional_words = [word for word in words if NRCLex(word).affect_list]
                #words = [w for w in words if w not in stopwords]

                freq_dict = Counter(emotional_words)
                #font_path = "assets/Roboto-Regular.ttf"

                if not freq_dict:
                    st.warning("No words found for the selected emotion.")
                else:
                    # Step 5: Generate and display wordcloud
                    wordcloud = WordCloud(
                        #font_path=font_path,
                        width=800,
                        height=400,
                        background_color=background_color,
                        max_words=100
                    ).generate_from_frequencies(freq_dict)

                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig)

            except Exception as e:
                st.error(f"Error generating word cloud: {e}")
        else:
            st.info("Please load data to see the word cloud.")


        with st.sidebar:

            st.subheader("Want to get book reccomendations?")
            #st.markdown("Click below to return to start.")
            if st.button(":books: Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True  # trigger recommendations fetch if needed
                st.rerun()

            st.subheader("Ready to explore another text?")
            #st.markdown("Click below to return to start.")
            if st.button(":repeat: Start Over"):
                st.session_state.clear()
                st.rerun()



    # === Emotions  Barplot ===

    elif selected_plot == "Barplot":
        st.subheader(friendly_plot_labels.get(selected_plot, selected_plot))

        with st.sidebar:
            st.subheader("🔧 Settings Menu")
            # Let user pick a bar color
            bar_color = st.color_picker(
                "Pick a bar color:",
                value="#FFC0CB",  # Default is pink
                key="bar_color_emotion_freq"
            )

            st.subheader("Want to get book reccomendations?")
            #st.markdown("Click below to return to start.")
            if st.button("📚 Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True  # trigger recommendations fetch if needed
                st.rerun()

            st.subheader("Ready to explore another text?")
            #st.markdown("Click below to return to start.")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()

        df1 = pd.DataFrame(novel_data)
       # st.subheader("Most Dominant Emotions")
        plot_emotion_frequency(df1, bar_color=bar_color)


    # === Emotion Mean Curve Plot ===

    elif selected_plot == "Curve":
        st.subheader(friendly_plot_labels.get(selected_plot, selected_plot))

        # Sidebar settings for color scale
        with st.sidebar:
            st.subheader("🔧 Settings Menu")
            color_scale_options = {
                "Vibrant": "Plotly",
                "Cool": "Viridis",
                "Warm": "Plasma",
                "Dark": "Inferno",
                "Classic": "Jet",
                "Rainbow": "Rainbow",
                "Red-Blue": "RdBu",
                "Portland": "Portland"
            }
            color_scale_label = st.selectbox(
                "Choose a color scale:",
                options=list(color_scale_options.keys()),
                key="color_scale_curve"
            )
            color_scale_curve = color_scale_options[color_scale_label]

            st.subheader("Want to get book recommendations?")
            if st.button("📚 Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True
                st.rerun()

            st.subheader("Ready to explore another text?")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()

        df1 = pd.DataFrame(novel_data)
        plot_emotion_evolution(df1, color_scale=color_scale_curve)



    # === Example sentences per emotion ===

    elif selected_plot == "Emotion Examples":

        st.subheader(friendly_plot_labels.get(selected_plot, selected_plot))

        # Extract emotion data
        novel_data = st.session_state.file_data
        # file_data["emotions"] is a list of dicts with at least "Predicted_Emotion" and "chunk"
        emotions_list = novel_data.get("emotions", [])

        # Get all unique emotions
        available_emotions = sorted(set(entry.get("Predicted_Emotion", "unknown") for entry in emotions_list))

        with st.sidebar:
            st.subheader("🔧 Settings Menu")
            selected_emotion = st.selectbox("Select an emotion:", available_emotions)
            num_examples = st.slider("Number of example sentences:", min_value=1, max_value=5, value=3, step=1)

        # Filter for selected emotion
        filtered = [entry for entry in emotions_list if entry.get("Predicted_Emotion") == selected_emotion]

        # Show max number of available examples for this emotion in the sidebar
        with st.sidebar:
            st.info(f"Maximum number of sentences for _{selected_emotion}_ is {len(filtered)}.")

        if not filtered:
            st.warning("No sentences found for this emotion.")
        else:
            st.markdown(f"**Showing {min(num_examples, len(filtered))} example sentences for _{selected_emotion}_:**")
            for i, entry in enumerate(filtered[:num_examples]):
                st.markdown(f"> {entry.get('chunk', '').strip()}")

        with st.sidebar:
            st.subheader("Want to get book reccomendations?")
            #st.markdown("Click below to return to start.")
            if st.button("📚 Get Similar Books"):
            # --- EDIT: set page to 'recommend_books' to show recommendations page ---
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True  # trigger recommendations fetch if needed
                st.rerun()

        with st.sidebar:
            st.subheader("Ready to explore another text?")
            #st.markdown("Click below to return to start.")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()


#################################################
# Page 4 – Plot poem Output
#################################################
elif st.session_state.page == "plot_poem":
    st.title("📝 Step 2: Explore the emotions in your poem")
    st.write("Dive into your poem’s emotional landscape. Choose a visualization to see how different feelings ebb and flow through the lines.")
    st.write("💡 We chunked your text input line by line, using the line breaks from the pasted text. **By default, one chunk equals one line.**")

    # 👉 Show sidebar menu only if file_data is present
    if st.session_state.get("poem_emotion_data") is not None:
        with st.sidebar:
            st.header("🔧 Settings Menu")
            #st.markdown("Use the sidebar to navigate or adjust plot settings.")

    else:
        st.error("No data source found. Please go back and enter a URL.")

    if st.session_state.get("poem_emotion_data") is not None:
        poem_data = st.session_state.poem_emotion_data  #Load poem data from session state

        if st.session_state.get("url"):
            url = st.session_state.url
            # Only fetch Gutenberg metadata if URL is from gutenberg.org
            if "gutenberg.org" in url:
                try:
                    book_id = url.strip("/").split("/")[-1]
                    meta_url = f"https://gutendex.com/books/{book_id}"
                    response = requests.get(meta_url)
                    response.raise_for_status()
                    metadata = response.json()
                    book_title = metadata.get("title", "Unknown Title")
                    authors = metadata.get("authors", [])
                    author_name = authors[0]["name"] if authors else "Unknown Author"
                    #cover_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"

                    st.write(f"📖 {book_title}")
                    st.write(f"✍️ {author_name}")
                    #st.image(cover_url, width=200)
                except Exception:
                    st.write("📖 Unknown Title")
                    st.write("✍️ Unknown Author")
            else:
                st.write("📖 Poem or non-Gutenberg text")

    else:
        st.error("No data source found. Please go back and enter a URL.")


    # Plot selection menu for poem
    selected_friendly_name = st.radio(
        "📋 Select a visualization",
        options=plot_options_display,
        #horizontal=True,
        key="poem_plot_selector"
    )

    selected_plot = next(
        (k for k, v in friendly_plot_labels.items() if v == selected_friendly_name),
        None
)
    if selected_plot is None:
        st.error("⚠️ Could not match selected plot option.")
        st.stop()

    st.subheader(friendly_plot_labels.get(selected_plot, selected_plot))
    st.divider()


    # === Interactive Plot ===

    # Available templates and plot types
    templates = ["plotly_dark",  "simple_white"] #"plotly_white",

    # Add this list of color scales (Plotly built-ins)
    color_scales = [
        "Plotly", "Viridis", "Plasma", "Inferno", "Jet", "Rainbow", "RdBu","Portland"
    ]


    if selected_plot == "Interactive Plot":
            with st.sidebar:
                #st.subheader("Interactive Plot Settings")
                chunks_interactive = st.number_input(
                    "How many grouped line(s) do you want to be displayed?",
                    min_value=1,
                    max_value=100,
                    value=1,
                    step=1,
                    key="chunks_interactive"
                )

                color_scale_options = {
                    "Vibrant": "Plotly",
                    "Cool": "Viridis",
                    "Warm": "Plasma",
                    "Dark": "Inferno",
                    "Classic": "Jet",
                    "Rainbow": "Rainbow",
                    "Red-Blue": "RdBu",
                    "Portland": "Portland"
                }
                color_scale_label = st.selectbox(
                    "Choose a color scale:",
                    options=list(color_scale_options.keys()),
                    key="color_scale_interactive"
                )
                color_scale_interactive = color_scale_options[color_scale_label]

                st.subheader("Ready to explore another text?")
                if st.button("🔁 Start Over"):
                    st.session_state.clear()
                    st.rerun()

            if st.session_state.get("poem_emotion_data") is not None:
                try:
                    # --- ADAPTED DATAFRAME CREATION ---
                    df_poem = pd.DataFrame(poem_data)
                    df_poem_other_model = pd.DataFrame.from_records(df_poem["emotions"].to_list())
                    is_poem = "line_text" in df_poem_other_model.columns

                    # Build emotion score DataFrame
                    poems_emotions_df = df_poem_other_model["Top_3_Emotions"].apply(pd.Series).fillna(0)

                    # Attach line text (for poems) or fallback chunk
                    if is_poem:
                        poems_emotions_df["chunk"] = df_poem_other_model["line_text"]
                    else:
                        poems_emotions_df["chunk"] = df_poem_other_model["chunk"]


                    poem_plot_stacked_emotions(
                        poems_emotions_df,
                        group_size=chunks_interactive,
                        color_scale=color_scale_interactive
                    )
                except Exception as e:
                    st.error(f"Error while plotting: {e}")

            else:
                st.info("Please upload a JSON file to see the plot.")


    # === Wordcloud ===
    elif selected_plot == "Wordcloud":
        with st.sidebar:
            #st.subheader("Wordcloud Settings")
            background_color = st.selectbox(
            "Background color:",
            ["white", "black"],
            key="bg_wc"
            )


        if st.session_state.get("poem_emotion_data") is not None:
            try:
                # Step 1: Extract the list of emotion entries
                poem_data = st.session_state.poem_emotion_data
                emotions_list = poem_data.get("emotions", [])

                # :mag: Get list of all unique dominant emotions
                available_emotions = sorted(set(entry.get("Predicted_Emotion", "unknown") for entry in emotions_list))

                # Define target emotions
                #target_emotions = {'anger', 'fear', 'surprise', 'sadness', 'joy', 'disgust'}

                #filtered_emotions = [entry for entry in emotions_list if entry.get("Predicted_Emotion") in target_emotions]
                #available_emotions2 = sorted(set(entry.get("Predicted_Emotion", "unknown") for entry in emotions_list if entry.get("Predicted_Emotion") not in ["neutral", "unknown"]))

                # Show all available emotions (excluding neutral/unknown)
                available_emotions2 = sorted(set(
                    get_emotion(entry)
                    for entry in emotions_list
                    if get_emotion(entry) not in ["neutral", "unknown"]
))

                # Select emotion to filter by
                with st.sidebar:
                    selected_emotion = st.selectbox("Filter wordcloud by dominant emotion:", ["All"] + available_emotions2)

                # Step 2: Filter entriess
                if selected_emotion != "All":
                    emotions_list = [entry for entry in emotions_list if get_emotion(entry) == selected_emotion]


                # Step 3: Combine all 'chunk' texts into one string
                all_text = " ".join(entry.get("line_text", "") for entry in emotions_list)


                # Step 4: Tokenize and count word frequencies
                stopwords =  ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as",
                              "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot",
                              "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each",
                              "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd",
                              "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
                              "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me",
                              "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
                              "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
                              "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
                              "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
                              "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
                              "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while",
                              "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
                              "you're", "you've", "your", "yours", "yourself", "yourselves"]

                # words = re.findall(r"\b[a-z]{3,}\b", all_text.lower())
                words = re.findall(r"\b\w{3,}\b", all_text)


                # Use NRCLex to determine emotional words
                emotional_words = [word for word in words if NRCLex(word).affect_list]
                #words = [w for w in words if w not in stopwords]

                freq_dict = Counter(emotional_words)

                if not freq_dict:
                    st.warning("No words found for the selected emotion.")
                else:
                    # Step 5: Generate and display wordcloud
                    wordcloud = WordCloud(
                        width=800,
                        height=400,
                        background_color=background_color,
                        max_words=100
                    ).generate_from_frequencies(freq_dict)

                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig)

            except Exception as e:
                st.error(f"Error generating word cloud: {e}")
        else:
            st.info("Please load data to see the word cloud.")


        with st.sidebar:

            st.subheader("Ready to explore another text?")
            #st.markdown("Click below to return to start.")
            if st.button(":repeat: Start Over"):
                st.session_state.clear()
                st.rerun()



    # === Emotions  Barplot ===

    elif selected_plot == "Barplot":

        with st.sidebar:
            #st.subheader("Emotion Intensity Settings")
            # Let user pick a bar color
            bar_color = st.color_picker(
                "Pick a bar color:",
                value="#FFC0CB",  # Default is pink
                key="bar_color_emotion_freq"
            )

            st.subheader("Ready to explore another text?")
            #st.markdown("Click below to return to start.")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()

        df1 = pd.DataFrame(poem_data)
       # st.subheader("Most Dominant Emotions")
        plot_emotion_frequency(df1, bar_color=bar_color)





    # === Emotion Mean Curve Plot ===

    elif selected_plot == "Curve":

        # Sidebar settings for color scale
        with st.sidebar:
            #st.subheader("Average Emotion Intensity Settings")
            color_scale_options = {
                "Vibrant": "Plotly",
                "Cool": "Viridis",
                "Warm": "Plasma",
                "Dark": "Inferno",
                "Classic": "Jet",
                "Rainbow": "Rainbow",
                "Red-Blue": "RdBu",
                "Portland": "Portland"
            }
            color_scale_label = st.selectbox(
                "Choose a color scale:",
                options=list(color_scale_options.keys()),
                key="color_scale_curve"
            )
            color_scale_curve = color_scale_options[color_scale_label]

            st.subheader("Ready to explore another text?")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()

        df1 = pd.DataFrame(poem_data)
        poem_plot_emotion_evolution(df1, color_scale=color_scale_curve)




    # === Example sentences per emotion ===

    elif selected_plot == "Emotion Examples":

        # Extract emotion data
        poem_data = st.session_state.poem_emotion_data
        # file_data["emotions"] is a list of dicts with at least "Predicted_Emotion" and "chunk"
        emotions_list = poem_data.get("emotions", [])

        # Get all unique emotions
        available_emotions = sorted(set(entry.get("Predicted_Emotion", "unknown") for entry in emotions_list))

        with st.sidebar:
            #st.subheader("🔍 Emotion Example Settings")
            selected_emotion = st.selectbox("Select an emotion:", available_emotions)
            num_examples = st.slider("Number of example line(s):", min_value=1, max_value=5, value=3, step=1)

        # Filter for selected emotion
        filtered = [entry for entry in emotions_list if entry.get("Predicted_Emotion") == selected_emotion]

        # Show max number of available examples for this emotion in the sidebar
        with st.sidebar:
            st.info(f"Maximum number of line(s) for _{selected_emotion}_ is {len(filtered)}.")

        if not filtered:
            st.warning("No line(s) found for this emotion.")
        else:
            st.markdown(f"**Showing {min(num_examples, len(filtered))} example sentences for _{selected_emotion}_:**")
            for i, entry in enumerate(filtered[:num_examples]):
                st.markdown(f"> {entry.get('line_text', '').strip()}")

        with st.sidebar:
            st.subheader("Ready to explore another text?")
            #st.markdown("Click below to return to start.")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()



#### Page 4: Recommendations
if st.session_state.page == "recommend_books":
    st.title("📚 Recommended Books")
    st.write("Here are some books similar to the one you analyzed:")

    if st.session_state.get("file_data") is not None:
        with st.sidebar:
            st.header("🔧 Settings Menu")

    else:
        st.error("No data source found. Please go back and enter a URL.")


    if "recommendations" in st.session_state:
        with st.sidebar:
            if st.button("Go to Plots"):
                st.session_state.page = "plot_novel"
                st.rerun()
            #st.markdown("Click below to return to start.")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()

        current_book_id = extract_book_id(st.session_state.url)

        # Filter for unique book_ids and remove the current book
        seen_ids = set()
        filtered_recs = []
        for rec in st.session_state.recommendations:
            rec_url = rec.get("url", "")
            book_id = extract_book_id(rec_url)
            if book_id and book_id != current_book_id and book_id not in seen_ids:
                filtered_recs.append(rec)
                seen_ids.add(book_id)
            if len(filtered_recs) == 3:
                break

        if not filtered_recs:
            st.warning("No valid recommendations to show.")
        else:
            for rec in filtered_recs:
                url = rec.get("url", "https://www.gutenberg.org")
                book_id = extract_book_id(url)
                similarity = rec.get("similarity", 0.0)

                # Fetch metadata
                title, author = get_book_metadata(book_id)
                cover_url = get_cover_url(book_id)

                # Display
                st.image(cover_url, width=120)
                st.markdown(f"### 📘 {title}")
                st.markdown(f"👤 *{author}*")
                st.markdown(f"🔗 **[View Book](https://www.gutenberg.org/ebooks/{book_id})**")
                st.markdown(f"**Similarity:** {similarity:.3f}")
                st.divider()
    else:
        st.warning("No recommendations available. Please analyze a text first.")
