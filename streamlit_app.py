import streamlit as st
import json
import plotly.graph_objects as go
import pandas as pd
import requests

from emotion_frequency import plot_emotion_frequency
from emotion_over_time import plot_emotion_evolution

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
        if st.button("Go to plots"):
            st.session_state.page = "plot"
            st.rerun()
        # Show Get Similar Books button
        if st.button("📚 Get Similar Books"):
            # --- EDIT: set page to 'recommend_books' to show recommendations page ---
            st.session_state.page = "recommend_books"
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

# Page 2 – Poem Input
# === MODIFIED: Poem input now uses a large text area instead of a URL ===
if st.session_state.page == "poem_input":
    st.title("📝 Step 1: Paste Your Poem")
    st.write("Paste your poem below. Ideal for shorter texts with emotional density.")

    # Large text area for poem input
    poem_text = st.text_area(
        "Paste your poem here:",
        height=300,  # Larger input window
        key="poem_text_input"
    )

    # Show funny GIF only before confirm
    if not st.session_state.confirm_clicked:
        st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")

    # Handle Confirm button
    if st.button("Confirm"):
        if poem_text.strip():
            st.session_state.confirm_clicked = True
            st.session_state.poem_text = poem_text
            st.rerun()
        else:
            st.error("Please paste your poem before continuing.")

    # ✅ After confirmation – fetch data and show info
    if st.session_state.confirm_clicked and poem_text and "file_data" not in st.session_state:
        with st.spinner("🔄 Analyzing text and extracting emotions..."):
            try:
                response = requests.post(
                    "https://emotionplot-api-znpzhhue6a-ew.a.run.app/analyze",
                    json={
                        "text": poem_text,
                        "sentences_per_chunk": 1,
                        "model": "accurate",
                    },
                    timeout=900,
                )
                response.raise_for_status()
                data = response.json()
                st.session_state.file_data = data
                st.session_state.poem_text = poem_text

                # Update progress bar
                progress_bar = st.progress(100)
                status_text = st.empty()
                status_text.text("✅ Done!")

                # No metadata for pasted poems
                st.write("📖 Custom Poem")
                st.write("✍️ Unknown Author")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ API request failed: {e}")

    # Next button
    if "file_data" in st.session_state:
        if st.button("Go to plots"):
            st.session_state.page = "plot"
            st.rerun()




#### Page 4: Recommendations
if st.session_state.page == "recommend_books":
    st.title("📚 Recommended Books")
    st.write("Here are some books similar to the one you analyzed:")

    if "recommendations" in st.session_state:
        for rec in st.session_state.recommendations:
            url = rec.get("book_url", "https://www.gutenberg.org")
            book_id = url.strip("/").split("/")[-1]
            similarity = rec.get("similarity", 0.0)

            st.markdown(f"🔗 **[View Book](https://www.gutenberg.org/ebooks/{book_id})**")
            st.markdown(f"**Similarity:** {similarity:.3f}")
            st.image(f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg", width=120)
            st.divider()
    else:
        st.warning("No recommendations available. Please analyze a text first.")
