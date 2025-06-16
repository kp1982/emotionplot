import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

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

    flat_rows = []                                                              # Flatten them into a single DataFrame
    for d in top3_dicts:
        for emotion, value in d.items():
            flat_rows.append({"emotion": emotion, "value": value})

    flat_df = pd.DataFrame(flat_rows)

    mean_emotions = flat_df.groupby("emotion")["value"].mean().sort_values(ascending=False)
                                                                                # Group and calculate mean

    fig, ax = plt.subplots(figsize=(10, 5))
    mean_emotions.plot(kind="bar", color=bar_color, edgecolor="black", ax=ax)   # CHANGE: ADD BAR_COLOR PARAMETER
    ax.set_title("Average Intensity of Emotions Across All Chunks")
    ax.set_xlabel("Emotion")
    ax.set_ylabel("Frequency of each emotion")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)
