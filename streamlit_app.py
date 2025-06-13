import streamlit as st
import json
import plotly.graph_objects as go
import pandas as pd
import requests



# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "input"

# Available templates and plot types
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
plot_types = ["Interactive Plot", "Wordcloud", "Barplot"]


#### put a maximus of chunks/groups so it doesnt go into negative

def plot_stacked_emotions(emotions_df, group_size=5, exclude_neutral=True, template_selected="plotly_white"):
    """
    Plots a stacked line chart of emotion scores from a DataFrame using Plotly.
    """
    # Select emotions to plot
    emotions_to_plot = [
        col for col in emotions_df.columns
        if col not in ["chunk", "text"] and not (exclude_neutral and col.lower() == "neutral")
    ]

    # Group emotion scores
    grouped = emotions_df[emotions_to_plot].groupby(emotions_df.index // group_size).sum()
    grouped["chunk"] = emotions_df["chunk"].groupby(emotions_df.index // group_size).first()

    # Custom emotion order (adjust to your data)
    custom_order = [
        "anger", "joy", "disapproval", "fear", "surprise", "curiosity", "sadness",
        "love", "gratitude", "pride", "relief", "amusement", "admiration", "approval",
        "excitement", "optimism", "caring", "desire", "realization", "confusion",
        "nervousness", "embarrassment", "annoyance", "disappointment", "remorse",
        "disgust", "grief", "neutral"
    ]
    default_visible = set(["anger", "joy", "disapproval", "fear", "surprise", "curiosity", "sadness"])

    fig = go.Figure()
    for emotion in custom_order:
        if emotion in grouped.columns:
            fig.add_trace(
                go.Scatter(
                    x=grouped.index,
                    y=grouped[emotion],
                    mode='lines',
                    name=emotion,
                    customdata=grouped["chunk"],
                    hovertemplate=(
                        "<b>Chunk Index:</b> %{x}<br>" +
                        "<b>Emotion:</b> %{fullData.name}<br>" +
                        "<b>Emotion Score:</b> %{y:.2f}<br>" +
                        "<b>Text:</b> %{customdata}<extra></extra>"
                    ),
                    visible=True if emotion in default_visible else "legendonly"
                )
            )

    fig.update_layout(
        title="Stacked Emotion Scores per Chunk",
        xaxis=dict(
            title="Chunk Index",
            rangeslider=dict(visible=True),
            type="linear"
        ),
        yaxis=dict(
            title="Emotion Score"
        ),
        height=600,
        legend_title="Emotion",
        dragmode="pan",
        template=template_selected
    )

    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

# Page 1 – URL or JSON Input
if st.session_state.page == "input":
    st.title("Emotionplot – Step 1")
    st.write("Please enter the URL:")

    url = st.text_input("Enter the URL of the novel/text:")

    if st.button("Confirm"):
        if url:
            params = {
                "url": url,
                "sentences_per_chunk": 5,
                "model": "accurate",
            }
            try:
                response = requests.get(
                    "https://emotionplot2-znpzhhue6a-ew.a.run.app/analyze",
                    params=params,
                    timeout=900,
                )
                response.raise_for_status()
                data = response.json()
                # Save API output to session_state
                st.session_state.file_data = data
                st.session_state.url = url
                st.success("API data loaded successfully!")
            except requests.exceptions.RequestException as e:
                st.error(f"API request failed: {e}")
        else:
            st.error("Please enter a URL before confirming.")


### end of new code ####


    file_data = None

    if st.button("Next"):
        if url and st.session_state.get("file_data") is not None:
            st.session_state.page = "plot"
            st.rerun()
        else:
            st.error("Please enter a valid URL.")


    # Display a funny looping GIF
    st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")


# Page 2 – Plot Output
elif st.session_state.page == "plot":
    st.title("Emotionplot – Step 2")

    if st.session_state.get("file_data") is not None:
        file_data = st.session_state.file_data  #Load saved data from session state

        if st.session_state.get("url"):
            st.write(f"Data loaded from URL: {st.session_state.url}")

        with st.expander("Show JSON Preview"):
            st.json(file_data)
    else:
        st.error("No data source found. Please go back and enter a URL.")

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
        if file_data is not None:
            try:
                # --- ADAPTED DATAFRAME CREATION ---
                df1 = pd.DataFrame(file_data)  # Step 1: Convert JSON to DataFrame
                df_other_model = pd.DataFrame.from_records(df1["emotions"].to_list())   # Step 2: Extract 'emotions' column and expand to DataFrame
                emotions_df = df_other_model["Top_3_Emotions"].apply(pd.Series).fillna(0)   # Step 3: Expand 'Top_3_Emotions' column into separate columns
                emotions_df["chunk"] = emotions_df.index  # Convert index to a column called 'chunk'

                plot_stacked_emotions(
                    emotions_df,
                    group_size=chunks_interactive,
                    template_selected=template_interactive
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
