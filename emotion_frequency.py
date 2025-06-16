import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def plot_emotion_frequency(data):

    df = pd.DataFrame(data["emotions"])                                         # Convert to DataFrame
    df["Top_3_Emotions"] = df["emotions"].apply(lambda x: x["Top_3_Emotions"])


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
    normalized_means = (grouped["chunk_normalized_score"]* 200).sort_values(ascending=False)

    # plt.figure(figsize=(10, 5))                                                 #Plot
    # mean_emotions.plot(kind="bar", color="pink", edgecolor="black")
    # plt.title("Average Intensity of Emotions Across All Chunks")
    # plt.xlabel("Emotion")
    # plt.ylabel("Frequency of each emotion")
    # plt.xticks(rotation=45, ha='right')
    # plt.tight_layout()
    # plt.grid(axis='y', linestyle='--', alpha=0.7)
    # #plt.show()
    # st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    normalized_means.plot(kind="bar", color="pink", edgecolor="black", ax=ax)
    ax.set_title("Average Intensity of Emotions Across all Chunks")
    ax.set_xlabel("Emotion")
    ax.set_ylabel("Frequency of each emotion")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)
