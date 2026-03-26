import streamlit as st
import pydeck as pdk
import pandas as pd

from eviction import borough_count, eviction

eviction_data = eviction()
eviction_data = eviction_data.dropna(subset=["latitude", "longitude"])

borough_count_clean = borough_count(eviction_data)

st.bar_chart(borough_count_clean, x="borough", y="Count")

df = eviction_data.copy()
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df = df.dropna(subset=["latitude", "longitude"])

layer = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position="[longitude, latitude]",
    radius_pixels=20,
    intensity=1,
    threshold=0.03,
    opacity=0.8,
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(
        latitude=40.7128,
        longitude=-74.0060,
        zoom=9.5,
    ),
    map_provider="carto",
    map_style="light",
)

st.pydeck_chart(deck)