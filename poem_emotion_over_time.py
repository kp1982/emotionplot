import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def poem_plot_emotion_evolution(df, default_emotion="amusement", color_scale="Plotly"):
    df["Top_3_Emotions"] = df["emotions"].apply(lambda x: x.get("Top_3_Emotions", {}))
    emotion_records = []
    for idx, row in df.iterrows():
        for emotion, score in row['Top_3_Emotions'].items():
            # Exclude neutral emotions
            if emotion.lower() == "neutral":
                continue
            emotion_records.append({
                'chunk': idx,
                'emotion': emotion,
                'score': score
            })

    emotion_df = pd.DataFrame(emotion_records)
    unique_emotions = sorted(emotion_df["emotion"].unique())

    # Choose color scale from Plotly
    color_scale_map = {
        "Plotly": px.colors.qualitative.Plotly,
        "Viridis": px.colors.sequential.Viridis,
        "Plasma": px.colors.sequential.Plasma,
        "Inferno": px.colors.sequential.Inferno,
        "Jet": px.colors.sequential.Jet,
        "Rainbow": px.colors.sequential.Rainbow,
        "RdBu": px.colors.diverging.RdBu,
        "Portland": px.colors.diverging.Portland,
    }
    px_colors = color_scale_map.get(color_scale, px.colors.qualitative.Plotly)
    emotion_colors = {emotion: px_colors[i % len(px_colors)] for i, emotion in enumerate(unique_emotions)}

    fig = go.Figure()
    for emotion in unique_emotions:
        emotion_data = emotion_df[emotion_df["emotion"] == emotion]
        fig.add_trace(go.Scatter(
            x=emotion_data["chunk"],
            y=emotion_data["score"],
            mode="lines+markers",
            name=emotion,
            line=dict(shape="spline", width=2, color=emotion_colors[emotion]),
            marker=dict(size=5),
            visible=True  # Alle Emotionen standardmäßig sichtbar
        ))

    max_score = emotion_df["score"].max() if not emotion_df.empty else 1
    fig.update_layout(
        #title="Emotional Evolution Over the Course of the Poem",
        xaxis_title="Text Chunk",
        yaxis_title="Emotion Intensity",
        yaxis=dict(range=[0, max_score]),
        template="plotly_white",
        height=500,
        legend_title="Click on emotions to show/hide",
    )

    st.plotly_chart(fig, use_container_width=True)
