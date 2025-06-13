import streamlit as st
import json
import plotly.graph_objects as go
import pandas as pd
import requests
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from collections import Counter
import time
import plotly.colors
from stacked_bar_plot import plot_stacked_emotions


# Page 1 - Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "input"
if "confirm_clicked" not in st.session_state:
    st.session_state.confirm_clicked = False

plot_types = ["Interactive Plot", "Wordcloud", "Barplot"]

# Page 1 – URL Input
if st.session_state.page == "input":
    st.title("Emotionplot – Step 1")
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

# After confirmation – fetch data and show book info
if st.session_state.confirm_clicked and "file_data" not in st.session_state:
    url = st.session_state.url

    # Actual API request
    status_text = st.empty()
    progress_bar = st.progress(0)

    with st.spinner("🔄 Analyzing text and extracting emotions..."):
        try:
            response = requests.get(
                "https://emotionplot2-znpzhhue6a-ew.a.run.app/analyze",
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
            progress_bar.progress(100)
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

                #st.success("✅ API data loaded successfully!")
                st.write(f"📖 {book_title}")
                st.write(f"✍️ {author_name}")
                st.image(cover_url, width=150)

            except Exception:
                status_text.text("✅ Done!")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ API request failed: {e}")

# Show "Go to plots" only after successful API response
if st.session_state.page == "input" and "file_data" in st.session_state:
    if st.button("Go to plots"):
        st.session_state.page = "plot"
        st.rerun()

# Page 2 – Plot Output
elif st.session_state.page == "plot":
    st.title("Emotionplot – Step 2")

    if st.session_state.get("file_data") is not None:
        file_data = st.session_state.file_data  #Load saved data from session state

        if st.session_state.get("url"):
            # st.write(f"Data loaded from URL: {st.session_state.url}")
            # Show book cover and book information for Gutenberg book
            book_id = st.session_state.url.strip("/").split("/")[-1]
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


        #with st.expander("Show JSON Preview"):
        #    st.json(file_data)
    else:
        st.error("No data source found. Please go back and enter a URL.")

    # Plot selection menu
    st.subheader("📋 Select Plot Type")
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
        st.subheader("📊 Interactive Plot")
        chunks_interactive = st.number_input(
            "How many groups of 5 sentences do you want to be displayed? (Interactive Plot)",
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            key="chunks_interactive"
        )
        # Map user-friendly names to Plotly templates
        template_options = {
            "Dark Mode": "plotly_dark",
            "White Mode": "simple_white"
        }
        template_interactive_label = st.selectbox(
            "Choose a plot template:",
            options=list(template_options.keys()),
            key="template_interactive"
        )
        template_interactive = template_options[template_interactive_label]
        # Map user-friendly names to Plotly color scales
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

        if file_data is not None:
            try:
                # --- ADAPTED DATAFRAME CREATION ---
                df1 = pd.DataFrame(file_data)
                df_other_model = pd.DataFrame.from_records(df1["emotions"].to_list())
                emotions_df = df_other_model["Top_3_Emotions"].apply(pd.Series).fillna(0)
                emotions_df["chunk"] = emotions_df.index

                plot_stacked_emotions(
                    emotions_df,
                    group_size=chunks_interactive,
                    template_selected=template_interactive,
                    color_scale=color_scale_interactive
                )
            except Exception as e:
                st.error(f"Error while plotting: {e}")
        else:
            st.info("Please upload a JSON file to see the plot.")




    # === Wordcloud ===
    elif selected_plot == "Wordcloud":
        st.subheader("☁️ Wordcloud")

        #max_words = st.slider(
        #    "Number of words in the Wordcloud:",
        #    #min_value=100,
        #    #max_value=000,
        #    value=100,
        #    step=10,
        #    key="max_words_wc"
        #)
        background_color = st.selectbox(
            "Background color:",
            ["white", "black"],
            key="bg_wc"
        )

        if file_data is not None:
            try:
                # Step 1: Extract the list of emotion entries
                emotions_list = file_data.get("emotions", [])

                # 🔍 Get list of all unique dominant emotions
                available_emotions = sorted(set(entry.get("Predicted_Emotion", "unknown") for entry in emotions_list))

                # Select emotion to filter by
                selected_emotion = st.selectbox("Filter wordcloud by dominant emotion:", ["All"] + available_emotions)

                # Step 2: Filter entries
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
                words = [w for w in words if w not in stopwords]

                freq_dict = Counter(words)

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

    # === Barplot ===
# elif selected_plot == "Barplot":
#        st.subheader("📶 Barplot")

#       chunks_bar = st.number_input(
#            "How many sentences should be grouped? (Barplot)",
#           min_value=1,
#            step=1,
#            key="chunks_bar"
#        )

#        st.write(f"Grouping: {chunks_bar}")
#        st.write("➡️ This is where the bar plot would appear.")

#    st.divider()

#if st.button("Back"):
#        st.session_state.page = "input"
#        st.rerun()
