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
from nrclex import NRCLex
import re
from utils import text_to_latex, latex_to_paragraph_dataframe

import subprocess
cmd = ['python3','-m','textblob.download_corpora']
subprocess.run(cmd)
print("Working")

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "start"
if "input_type" not in st.session_state:
    st.session_state.input_type = None



# Available templates and plot types
plot_types = ["Interactive Plot", "Wordcloud", "Barplot", "Curve", "Emotion Examples"]



# Page 0 – Selection of text type
if st.session_state.page == "start":
    st.title("📚 Welcome to Emotionplot")
    st.write("Uncover the emotional journey in literature. Choose your type of text to begin:")

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



# Page 1 – Novel Input
if "page" not in st.session_state:
    st.session_state.page = "input"
if "confirm_clicked" not in st.session_state:
    st.session_state.confirm_clicked = False

# Page 1 – URL novel_input
if "page" not in st.session_state:
    st.session_state.page = "input"
if "confirm_clicked" not in st.session_state:
    st.session_state.confirm_clicked = False

# Page 1 – URL novel_input
if st.session_state.page == "novel_input":
    st.title("📖 Step 1: Paste Your Novel Link")
    st.write("Paste a URL from **Project Gutenberg** or another online source. We'll fetch the text and analyze its emotions.")

    # st.write("Please enter the URL:")

    url = st.text_input("Enter the URL of the novel/text:")

    # Show funny GIF only before confirm
    if not st.session_state.confirm_clicked:
        st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")

    # Handle Confirm button
    if st.button("Confirm"):
        if url:
            st.session_state.confirm_clicked = True
            st.session_state.url = url
            st.rerun()
        else:
            st.error("Please enter a valid URL.")

    # ✅ After confirmation – fetch data and show book info
    if st.session_state.confirm_clicked and url and "file_data" not in st.session_state:
        # Actual API request
        with st.spinner("🔄 Analyzing text and extracting emotions..."):
            try:
                response = requests.get(
                    "https://emotionplot-api-znpzhhue6a-ew.a.run.app/analyze",
                    params={
                        "url": url,
                        "sentences_per_chunk": 5,
                        "model": "accurate",
                    },
                    timeout=900,
                )
                response.raise_for_status()
                data = response.json()
                st.session_state.file_data = data
                st.session_state.url = url

                # Update progress bar
                progress_bar = st.progress(100)
                status_text = st.empty()
                status_text.text("✅ Done!")


                # Fetch metadata
                try:
                    book_id = url.strip("/").split("/")[-1]
                    meta_url = f"https://gutendex.com/books/{book_id}"
                    meta_response = requests.get(meta_url)
                    meta_response.raise_for_status()
                    metadata = meta_response.json()

                    book_title = metadata.get("title", "Unknown Title")
                    authors = metadata.get("authors", [])
                    author_name = authors[0]["name"] if authors else "Unknown Author"
                    cover_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"

                    # Display book info and cover side by side (only once)
                    info_col, cover_col = st.columns([2, 1])
                    with info_col:
                        st.write(f"📖 {book_title}")
                        st.write(f"✍️ {author_name}")
                    with cover_col:
                        st.image(cover_url, width=150)

                except Exception:
                    status_text.text("✅ Done!")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ API request failed: {e}")

    # Next button
    if "file_data" in st.session_state:
        if st.button("🚀 Go to plots"):
            st.session_state.page = "plot_novel" ###### --- EDIT: changed to 'plot_novel' ---
            st.rerun()
        # Show Get Similar Books button
        if st.button("📚 Get Similar Books"):
            st.session_state.page = "recommend_books"  # set page to 'recommend_books' to show recommendations page
            st.session_state.recommend_clicked = True  # trigger recommendations fetch if needed
            st.rerun()

        ## additional button to start over
        # if st.button("🔄 Start Over"):
        #     for key in ["file_data", "emotions", "recommend_clicked", "recommendations"]:
        #         st.session_state.pop(key, None)
        #     st.rerun()

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
    st.title("📝 Step 1: Paste Your Poem")
    st.write("Paste your poem below. Ideal for shorter texts with emotional density.")
    # Large text area for poem input
    poem_text = st.text_area(
        "Paste your poem here:",
        height=300,  # Larger input window
        key="poem_text_input"
    )
    # Show funny GIF only before confirmation
    if not st.session_state.confirm_clicked:
        st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")

    # Confirm button
    if st.button("Confirm"):
        if poem_text.strip():
            st.session_state.confirm_clicked = True
            st.session_state.poem_latex = text_to_latex(poem_text)
            st.session_state.paragraph_df = latex_to_paragraph_dataframe(st.session_state.poem_latex)
            st.rerun()
        else:
            st.error("Please paste your poem before continuing.")

    # After confirmation, fetch emotion data if not already present
    if st.session_state.confirm_clicked and "poem_emotion_data" not in st.session_state:
        try:
            with st.spinner("🔄 Analyzing emotions in your poem..."):
                response = requests.get(
                    "https://emotionplot-api-644268373090.europe-west1.run.app/analyze_poemlines/",
                    params={"poem_text": st.session_state.poem_latex, "model": "accurate"},
                    timeout=1800
                )
                response.raise_for_status()
                data = response.json()
                st.session_state.poem_emotion_data = data

                # Update progress bar
                progress_bar = st.progress(100)
                status_text = st.empty()

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Emotion analysis failed: {e}")
            st.stop()
        st.rerun()

    # Next button and "Done" status
    if st.session_state.confirm_clicked and "poem_emotion_data" in st.session_state:
        st.text("✅ Done!")
        if st.button("🚀 Go to plots"):
            st.session_state.page = "plot_poem"  # --- EDIT: changed to 'plot_poem' ---
            st.rerun()

#################################################
# Page 3 – Plot Output Novel
#################################################
elif st.session_state.page == "plot_novel":
    st.title("📖 Step 2: Explore the Emotions of the Novel")
    st.write("Choose a visualization below to see how emotions unfold in your text.")

    # 👉 Show sidebar menu only if file_data is present
    if st.session_state.get("file_data") is not None:
        with st.sidebar:
            st.header("🔧 Settings Menu")
            #st.markdown("Use the sidebar to navigate or adjust plot settings.")

    else:
        st.error("No data source found. Please go back and enter a URL.")

    if st.session_state.get("file_data") is not None:
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




    # Plot selection menu
    st.subheader("📋 Select Output Type")
    selected_plot = st.radio("Choose a plot:", options=plot_types, horizontal=True)
    st.divider()


    # === Interactive Plot ===

    # Available templates and plot types
    templates = ["plotly_dark",  "simple_white"] #"plotly_white",

    # Add this list of color scales (Plotly built-ins)
    color_scales = [
        "Plotly", "Viridis", "Plasma", "Inferno", "Jet", "Rainbow", "RdBu","Portland"
    ]


    if selected_plot == "Interactive Plot":
        st.subheader("📊 Stacked Emotion Scores by Sentence Groups")
        with st.sidebar:
            st.subheader("Interactive Plot Settings")
            chunks_interactive = st.number_input(
                "How many groups sentences do you want to be displayed?",
                min_value=1,
                max_value=100,
                value=10,
                step=1,
                key="chunks_interactive"
            )

            # Map user-friendly names to Plotly templates
            # template_options = {
            #     "Dark Mode": "plotly_dark",
            #     "White Mode": "simple_white"
            # }
            # template_interactive_label = st.selectbox(
            #     "Choose a plot template:",
            #     options=list(template_options.keys()),
            #     key="template_interactive"
            # # )
            # template_interactive = template_options[template_interactive_label]

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

            st.subheader("Want to get book reccomendations?")
            if st.button("📚 Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True
                st.rerun()

            st.subheader("Ready to explore another text?")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()



        if st.session_state.get("file_data") is not None:
            try:
                # --- ADAPTED DATAFRAME CREATION ---
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

        else:
            st.info("Please upload a JSON file to see the plot.")




    # === Wordcloud ===
    elif selected_plot == "Wordcloud":
        st.subheader("☁️ Emotion Wordcloud")

        with st.sidebar:
            st.subheader("Wordcloud Settings")
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

            st.subheader("Want to get book reccomendations?")
            #st.markdown("Click below to return to start.")
            if st.button(":books: Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True  # trigger recommendations fetch if needed
                st.rerun()

            st.subheader(":rocket: Ready to explore another text?")
            st.markdown("Click below to return to start.")
            if st.button(":repeat: Start Over"):
                st.session_state.clear()
                st.rerun()



    # === Emotions  Barplot ===

    elif selected_plot == "Barplot":
        st.subheader("📶 Average Intensity of Emotions across the Text")


        with st.sidebar:
            st.subheader("Emotion Intensity Settings")
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
        st.subheader("📈 Tracking Emotional Shifts Across the Novel")

        # Sidebar settings for color scale
        with st.sidebar:
            st.subheader("Emotional Shifts Settings")
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


            st.subheader("Want to get book reccomendations?")
            if st.button("📚 Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True  # trigger recommendations fetch if needed
                st.rerun()

            st.subheader("Ready to explore another text?")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()

        df1 = pd.DataFrame(novel_data)
        plot_emotion_evolution(df1, color_scale=color_scale_curve)



    # === Example sentences per emotion ===

    elif selected_plot == "Emotion Examples":
        st.subheader("🔍 Example Sentences by Emotion")

        # Extract emotion data
        novel_data = st.session_state.file_data
        # file_data["emotions"] is a list of dicts with at least "Predicted_Emotion" and "chunk"
        emotions_list = novel_data.get("emotions", [])

        # Get all unique emotions
        available_emotions = sorted(set(entry.get("Predicted_Emotion", "unknown") for entry in emotions_list))

        with st.sidebar:
            st.subheader("Emotion Example Settings")
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
    st.title("📝 Step 2: Explore the Emotions of a Poem")
    st.write("Choose a visualization below to see how emotions unfold in your poem.")

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




    # Plot selection menu
    st.subheader("📋 Select Output Type")
    selected_plot = st.radio("Choose a plot:", options=plot_types, horizontal=True)
    st.divider()


    # === Interactive Plot ===

    # Available templates and plot types
    templates = ["plotly_dark",  "simple_white"] #"plotly_white",

    # Add this list of color scales (Plotly built-ins)
    color_scales = [
        "Plotly", "Viridis", "Plasma", "Inferno", "Jet", "Rainbow", "RdBu","Portland"
    ]


    if selected_plot == "Interactive Plot":
        st.subheader("📊 Stacked Emotion Scores by Sentence Groups")
        with st.sidebar:
            st.subheader("Interactive Plot Settings")
            chunks_interactive = st.number_input(
                "How many groups sentences do you want to be displayed?",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                key="chunks_interactive"
            )

            # Map user-friendly names to Plotly templates
            # template_options = {
            #     "Dark Mode": "plotly_dark",
            #     "White Mode": "simple_white"
            # }
            # template_interactive_label = st.selectbox(
            #     "Choose a plot template:",
            #     options=list(template_options.keys()),
            #     key="template_interactive"
            # # )
            # template_interactive = template_options[template_interactive_label]

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

            st.subheader("Want to get book reccomendations?")
            if st.button("📚 Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True
                st.rerun()

            st.subheader("Ready to explore another text?")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()

        if st.session_state.get("poem_emotion_data") is not None:
            try:
                # --- ADAPTED DATAFRAME CREATION ---
                df1 = pd.DataFrame(poem_data)
                df_other_model = pd.DataFrame.from_records(df1["emotions"].to_list())
                emotions_df = df_other_model["Top_3_Emotions"].apply(pd.Series).fillna(0)
                emotions_df["chunk"] = emotions_df.index

                poem_plot_stacked_emotions(
                    emotions_df,
                    group_size=chunks_interactive,
                    color_scale=color_scale_interactive
                )
            except Exception as e:
                st.error(f"Error while plotting: {e}")

        else:
            st.info("Please upload a JSON file to see the plot.")




    # === Wordcloud ===
    elif selected_plot == "Wordcloud":
        st.subheader("☁️ Emotion Wordcloud")

        #max_words = st.slider(
        #    "Number of words in the Wordcloud:",
        #    #min_value=100,
        #    #max_value=000,
        #    value=100,
        #    step=10,
        #    key="max_words_wc"
        #)
        with st.sidebar:
            st.subheader("Wordcloud Settings")
            background_color = st.selectbox(
            "Background color:",
            ["white", "black"],
            key="bg_wc"
            )


        if st.session_state.get("poem_emotion_data") is not None:
            try:
                # Step 1: Extract the list of emotion entries
                emotions_list = poem_data.get("emotions", [])

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

            st.subheader("Want to get book reccomendations?")
            #st.markdown("Click below to return to start.")
            if st.button(":books: Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True  # trigger recommendations fetch if needed
                st.rerun()

            st.subheader(":rocket: Ready to explore another text?")
            st.markdown("Click below to return to start.")
            if st.button(":repeat: Start Over"):
                st.session_state.clear()
                st.rerun()



    # === Emotions  Barplot ===

    elif selected_plot == "Barplot":
        st.subheader("📶 Average Intensity of Emotions across the Text")


        with st.sidebar:
            st.subheader("Emotion Intensity Settings")
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

        df1 = pd.DataFrame(poem_data)
       # st.subheader("Most Dominant Emotions")
        plot_emotion_frequency(df1, bar_color=bar_color)





    # === Emotion Mean Curve Plot ===

    elif selected_plot == "Curve":
        st.subheader("📈 Tracking Emotional Shifts Across the Novel")

        # Sidebar settings for color scale
        with st.sidebar:
            st.subheader("Average Emotion Intensity Settings")
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


            st.subheader("Want to get book reccomendations?")
            if st.button("📚 Get Similar Books"):
                st.session_state.page = "recommend_books"
                st.session_state.recommend_clicked = True  # trigger recommendations fetch if needed
                st.rerun()

            st.subheader("Ready to explore another text?")
            if st.button("🔁 Start Over"):
                st.session_state.clear()
                st.rerun()

        df1 = pd.DataFrame(poem_data)
        poem_plot_emotion_evolution(df1, color_scale=color_scale_curve)




    # === Example sentences per emotion ===

    elif selected_plot == "Emotion Examples":
        st.subheader("🔍 Example Sentences by Emotion")

        # Extract emotion data
        poem_data = st.session_state.poem_emotion_data
        # file_data["emotions"] is a list of dicts with at least "Predicted_Emotion" and "chunk"
        emotions_list = poem_data.get("emotions", [])

        # Get all unique emotions
        available_emotions = sorted(set(entry.get("Predicted_Emotion", "unknown") for entry in emotions_list))

        with st.sidebar:
            st.subheader("🔍 Emotion Example Settings")
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
            st.markdown("Click below to return to start.")
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
