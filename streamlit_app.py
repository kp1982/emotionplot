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



# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "start"
if "input_type" not in st.session_state:
    st.session_state.input_type = None


plot_types = ["Interactive Plot", "Wordcloud", "Barplot"]


# Page 0 – Auswahl der Textart
if st.session_state.page == "start":
    st.title("Emotionplot – Welcome!")
    st.write("What type of text would you like to analyze?")

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

# Page 1 - Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "input"
if "confirm_clicked" not in st.session_state:
    st.session_state.confirm_clicked = False

# Page 1 – URL novel_input
if st.session_state.page == "novel_input":
    st.title("Emotionplot – Step 1: Novel Input")
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

                    #st.success("✅ API data loaded successfully!")
                    st.write(f"📖 {book_title}")
                    st.write(f"✍️ {author_name}")
                    st.image(cover_url, width=150)

                except Exception:
                    status_text.text("✅ Done!")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ API request failed: {e}")

    # Next button
    if "file_data" in st.session_state:
        if st.button("Go to plots"):
            st.session_state.page = "plot"
            st.rerun()
            #else:
            #   st.error("Please confirm a valid URL before continuing.")

# Page 2 – Poem Input
if st.session_state.page == "poem_input":
    st.title("Emotionplot – Step 1: Poem Input")
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
                    "https://emotionplot2-znpzhhue6a-ew.a.run.app/analyze",
                    params={
                        "url": url,
                        "sentences_per_chunk": 1,
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

                    #st.success("✅ API data loaded successfully!")
                    st.write(f"📖 {book_title}")
                    st.write(f"✍️ {author_name}")
                    st.image(cover_url, width=150)

                except Exception:
                    status_text.text("✅ Done!")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ API request failed: {e}")

    # Next button
    if "file_data" in st.session_state:
        if st.button("Go to plots"):
            st.session_state.page = "plot"
            st.rerun()
            #else:
            #   st.error("Please confirm a valid URL before continuing.")


# Page 3 – Plot Output
elif st.session_state.page == "plot":
    st.title("Emotionplot – Step 2")

    if st.session_state.get("file_data") is not None:
        file_data = st.session_state.file_data  #Load saved data from session state

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

        if file_data is not None:
            try:
                # Step 1: Extract the list of emotion entries
                emotions_list = file_data.get("emotions", [])

                # Step 2: Combine all 'chunk' texts into one string
                all_text = " ".join(entry.get("chunk", "") for entry in emotions_list)

                # Step 3 (alt): Tokenize and count word frequencies
                words = re.findall(r"\b[a-z]{3,}\b", all_text)  # filter to words of 3+ letters
                freq_dict = Counter(words)

                # Step 4 (alt): Generate from frequencies
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color=background_color,
                    max_words=max_words
                ).generate_from_frequencies(freq_dict)

                # Step 3: Generate and display wordcloud
                #wordcloud = WordCloud(
                #    width=800,
                #    height=400,
                #    background_color=background_color,
                #    max_words=max_words
                #).generate(all_text)

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
