import pandas as pd
#import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px

def plot_emotion_frequency(data, bar_color="pink"):    # CHANGE: ADD BAR_COLOR PARAMETER
    """
    Plots the average intensity of emotions across all chunks.
    Parameters:
        data (dict): The input data containing emotions.
        bar_color (str): The color of the bars in the plot. Default is "pink".
    """

    df = pd.DataFrame(data["emotions"])                                         # Convert to DataFrame
    df["Top_3_Emotions"] = df["emotions"].apply(lambda x: x["Top_3_Emotions"])

    top3_dicts = df["Top_3_Emotions"].tolist()                                  # Extract list of all top3 emotion dicts


    top3_dicts = df["Top_3_Emotions"].tolist()                                  #Extract list of all top3 emotion dicts

    flat_rows = []                                                              #Flatten them into a single DataFrame
    for idx, d in enumerate(top3_dicts):
        for emotion, value in d.items():
            flat_rows.append({"chunk": idx, "emotion": emotion, "value": value})

    flat_df = pd.DataFrame(flat_rows)
    flat_df = flat_df[flat_df["emotion"].notna() & flat_df["value"].notna()]


    #mean_emotions = flat_df.groupby("emotion")["value"].mean().sort_values(ascending=False)
                                                                                #Group and calculate mean
    total_chunks = df.shape[0]

    # Step 4: Group by emotion
    grouped = flat_df.groupby("emotion").agg(
        total_score=("value", "sum"),
        appearance_count=("chunk", "nunique")
    )
    grouped = grouped[grouped.index != "neutral"]

    # Step 5: Normalize by total chunks (not just where emotion appeared)
    grouped["chunk_normalized_score"] = grouped["total_score"] / total_chunks

    # Optional: sort for plotting or display
    normalized_means = (grouped["chunk_normalized_score"]* 100).sort_values(ascending=False)

    # fig, ax = plt.subplots(figsize=(10, 5))
    # normalized_means.plot(kind="bar", color=bar_color, edgecolor="black", ax=ax)# CHANGE: ADD BAR_COLOR PARAMETER
    # ax.set_title("Average Intensity of Emotions Across all Chunks")

    # ax.set_xlabel("Emotion")
    # ax.set_ylabel("Frequency of each emotion")
    # plt.xticks(rotation=45, ha='right')
    # plt.tight_layout()
    # plt.grid(axis='y', linestyle='--', alpha=0.7)

    # st.pyplot(fig)

    fig = px.bar(
    normalized_means.reset_index(),
    x="emotion",
    y="chunk_normalized_score",
    text=normalized_means.round(2),
    color_discrete_sequence=[bar_color],
    labels={"chunk_normalized_score": "Normalized Score (%)", "emotion": "Emotion"},
    hover_data={"emotion": True, "chunk_normalized_score": True}
)

    #fig.update_traces(texttemplate='%{x}<br>%{y:.2f}%', textposition='outside')
    fig.update_layout(
        title="📊 Average Intensity of Emotions Across All Chunks",
        xaxis_title="Emotion",
        yaxis_title="Normalized Frequency (%)",
        yaxis=dict(range=[0, max(normalized_means) * 1.15]),
        bargap=0.3,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
