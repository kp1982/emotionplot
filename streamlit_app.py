import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "input"

# Available templates and plot types
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
plot_types = ["Interactive Plot", "Wordcloud", "Barplot"]

# df = pd.read_csv('data/...')

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "input"

# Available templates and plot types
templates = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
plot_types = ["Interactive Plot", "Wordcloud", "Barplot"]

# Page 1 – URL Input
if st.session_state.page == "input":
    st.title("Emotionplot – Step 1")
    st.write("Please enter the URL:")

    url = st.text_input("Enter URL")

    if st.button("Next"):
        if url:
            st.session_state.url = url
            st.session_state.page = "plot"
            st.experimental_rerun()
        else:
            st.error("Please enter a valid URL.")

    #st.divider()
    #st.markdown("#### 🐵 While you're waiting, enjoy this GIF:")
    
    # Display a funny looping GIF
    st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjZjNWw3cHkxOXZ5dDRzZWMxbThwZ3ZiNXJhOW5jZnJudTloOWY1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif")


# Page 2 – Plot Output
elif st.session_state.page == "plot":
    st.title("Emotionplot – Step 2")
    st.write(f"🔗 URL: {st.session_state.url}")

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


def plot_stacked_emotions(df, group_size=5, exclude_neutral=True):
    """
    Plots a stacked bar chart of emotion scores from a DataFrame using Plotly.

    Parameters:
    - emotions_df (pd.DataFrame): A DataFrame containing emotion scores per chunk.
    - group_size (int): Number of chunks to group together for aggregation.
    - exclude_neutral (bool): Whether to exclude the "neutral" emotion from the plot.

    Returns:
    - None (shows an interactive plot)
    """
    # Select emotions to plot
    emotions_to_plot = [
        col for col in df.columns
     #   if not (exclude_neutral and col.lower() == "neutral")
    ]

    # Group emotion scores
    grouped = df[emotions_to_plot].groupby(df.index // group_size).sum()

    template_to_select = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
    template_selected = "plotly_white"

    #fig = go.Figure()

    default_visible = ["anger", "joy", "disapproval", "fear", "surprise", "curiosity", "sadness"]  # Emotions to show by default


    # Your custom emotion order (must match column names in emotions_df)
    custom_order = [
        "anger", "joy", "disapproval", "fear", "surprise", "curiosity", "sadness"
        'love',
        'gratitude',
        'pride',
        'relief',
        'amusement',
        'admiration',
        'approval',
        'excitement',
        'optimism',
        'caring',
        'desire',
        'realization',
        'confusion',
        'nervousness',
        'embarrassment',
        'annoyance',
        'disappointment',
        'remorse',
        'disgust',
        'grief',
        'neutral'
    ]


# Loop through custom order
for emotion in custom_order:
    if emotion in emotions_df.columns:
        fig.add_trace(
            go.Scatter(
                x=emotions_df.index,
                y=emotions_df[emotion],
                mode='lines',
                name=emotion,
                customdata=df["chunk"],
                hovertemplate=(
                    "<b>Chunk Index:</b> %{x}<br>" +
                    "<b>Emotion:</b> %{fullData.name}<br>" +
                    "<b>Emotion Score:</b> %{y:.2f}<br>" +
                    "<b>Text:</b> %{customdata}<extra></extra>"
                ),
                visible=True if emotion in default_visible else "legendonly"
            )
        )

    # Configure layout
    fig.update_layout(
        barmode='stack',
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

    fig.show(config={"scrollZoom": True})


    # === Wordcloud ===
    elif selected_plot == "Wordcloud":
        st.subheader("☁️ Wordcloud")

        max_sentences = st.slider(
            "Number of sentences in the Wordcloud:",
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

#plot_stacked_emotions(df)

def generate_wordclouds(df, chunk_size):
    """
    Generates word clouds for grouped sentences.

    Parameters:
    - df (pd.DataFrame): DataFrame containing sentences and emotional words.
    - chunk_size (int): Number of sentences per group.

    Returns:
    - Displays word clouds for each sentence group.
    """

    # Assign sentence groups dynamically based on chunk size
    df["Sentence_Group"] = df.index // chunk_size

    # Group emotional words by sentence group
    grouped_words = df.groupby("Sentence_Group")["words"].apply(lambda x: " ".join(x)).reset_index()

    # Create word clouds for each sentence group
    fig, axes = plt.subplots(1, len(grouped_words), figsize=(15, 6))

    # Generate word cloud for each sentence group
    for i, row in grouped_words.iterrows():
        #wordcloud = WordCloud(width=400, height=400, background_color="white").generate(row["words"])
        #axes[i].imshow(wordcloud, interpolation="bilinear")
        #axes[i].axis("off")
        #axes[i].set_title(f"Chunk {row['Sentence_Group']}")

    # Show the word clouds
    plt.tight_layout()
    plt.show()


#generate_wordclouds(df, max_sentences)


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
