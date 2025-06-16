import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def plot_emotion_evolution(df, default_emotion="amusement"):

    df["Top_3_Emotions"] = df["emotions"].apply(lambda x: x.get("Top_3_Emotions", {}))
    emotion_records = []                                                        #Flatten Top_3_Emotions into a long-form DataFrame
    for idx, row in df.iterrows():
        for emotion, score in row['Top_3_Emotions'].items():
            emotion_records.append({
                'chunk': idx,
                'emotion': emotion,
                'score': score
            })

    emotion_df = pd.DataFrame(emotion_records)


    unique_emotions = sorted(emotion_df["emotion"].unique())                    #Get all unique emotions and assign colors

    px_colors = px.colors.qualitative.T10 + px.colors.qualitative.Dark24 + px.colors.qualitative.Pastel
    emotion_colors = {emotion: px_colors[i % len(px_colors)] for i, emotion in enumerate(unique_emotions)}


    fig = go.Figure()                                                           #Create the plot with only one shown by default

    # for emotion in unique_emotions:
    #     emotion_data = emotion_df[emotion_df["emotion"] == emotion]
    #     fig.add_trace(go.Scatter(
    #         x=emotion_data["chunk"],
    #         y=emotion_data["score"],
    #         mode="lines+markers",
    #         name=emotion,
    #         line=dict(shape="spline", width=2, color=emotion_colors[emotion]),
    #         marker=dict(size=5),
    #         visible=True if emotion == default_emotion else "legendonly"
    #     ))


    # fig.update_layout(                                                          #Final layout
    #     title="📈 Emotion Evolution Over Time",
    #     xaxis_title="Emotional Progression Over Time (Chunks)",
    #     yaxis_title="Emotion Intensity",
    #     yaxis=dict(range=[0, 1]),
    #     template="plotly_white",
    #     height=500,
    #     legend_title="Click emotions to toggle",
    # )

    # fig.show()

    for emotion in unique_emotions:
        emotion_data = emotion_df[emotion_df["emotion"] == emotion]
        fig.add_trace(go.Scatter(
        x=emotion_data["chunk"],
        y=emotion_data["score"],
        mode="lines+markers",
        name=emotion,
        line=dict(shape="spline", width=2, color=emotion_colors[emotion]),
        marker=dict(size=5),
        visible=True if emotion == default_emotion else "legendonly"
    ))

    fig.update_layout(
    title="📈 Emotion Evolution Over Time",
    xaxis_title="Emotional Progression Over Time (Chunks)",
    yaxis_title="Emotion Intensity",
    yaxis=dict(range=[0, 1]),
    template="plotly_white",
    height=500,
    legend_title="Click emotions to toggle",   )

    st.plotly_chart(fig, use_container_width=True)
