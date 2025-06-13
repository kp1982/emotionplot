import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.colors


####Plot

def plot_stacked_emotions(emotions_df, group_size=1, exclude_neutral=False, template_selected="plotly_dark", color_scale="Plotly"):
    """
    Plots a stacked line chart of emotion scores from a DataFrame using Plotly.
    Restricts zoom out so x-axis does not go into negative values.
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
        "neutral", "grief", "disgust", "remorse", "disappointment", "annoyance",
        "embarrassment", "nervousness", "confusion", "realization", "desire",
        "caring", "optimism", "excitement", "approval", "admiration", "amusement",
        "relief", "pride", "gratitude", "love", "sadness", "curiosity", "surprise",
        "fear", "disapproval", "joy", "anger"
    ]
    default_visible = set(["anger", "joy", "disapproval", "fear", "surprise", "curiosity", "sadness"])

    # Get color scale from Plotly
    try:
        colors = plotly.colors.get_colorscale(color_scale.lower())
    except Exception:
        # fallback to Plotly default if not found
        colors = plotly.colors.qualitative.Plotly

    # If not a continuous scale, use qualitative
    if isinstance(colors, list) and isinstance(colors[0], str):
        color_list = colors
    else:
        # If it's a list of [value, color], extract just the colors
        color_list = [c[1] for c in colors]

    fig = go.Figure()
    emotion_count = sum([1 for emotion in custom_order if emotion in grouped.columns])
    for idx, emotion in enumerate(custom_order):
        if emotion in grouped.columns:
            color = color_list[idx % len(color_list)]
            fig.add_trace(
                go.Bar(
                    x=grouped.index,
                    y=grouped[emotion],
                    name=emotion,
                    marker_color=color,
                    hovertemplate=(
                        "<b>Emotion:</b> %{fullData.name}<br>" +
                        "<b>Emotion Score:</b> %{y:.2f}<br>"
                    ),
                    visible=True if emotion in default_visible else "legendonly"
                )
            )

    # Restrict zoom out: set xaxis range and constrain
    min_x = grouped.index.min()
    max_x = grouped.index.max()
    fig.update_layout(
        barmode='stack',
        title="Stacked Emotion Scores per Chunk",
        xaxis=dict(
            title=f"{group_size * 5} sentences per chunk",
            rangeslider=dict(visible=True),
            type="linear",
            range=[min_x, max_x],
            fixedrange=True,
            rangebreaks=[dict(bounds=[-float("inf"), 0])]
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
