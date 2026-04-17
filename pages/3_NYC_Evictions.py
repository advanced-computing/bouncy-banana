import time
from contextlib import contextmanager

import folium
import streamlit as st
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium

from eviction import borough_count, eviction
from utils.styles import apply_global_styles

apply_global_styles()


@st.cache_data(ttl=3600)
def load_eviction_data():
    df = eviction()
    df = df.dropna(subset=["latitude", "longitude"])
    return df


eviction_data = load_eviction_data()

st.title("Evictions and Unemployment in NYC (2017-Present)")

st.markdown(
    """
    <div style="
        background-color:#93b9e1;
        padding:20px;
        border-radius:8px;
        border-left:6px solid #0f0f59;
        font-size:17px;
        color: 93b9e1;
    ">
        This page explores the relationship between unemployment and housing
        evictions in New York City over time. Our data on evictions in New York City
        comes from NYC Open Data and spans across the five boroughs from 2017 to present.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.subheader("NYC Evictions 2017-Present by Geography")


nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

points = eviction_data[["latitude", "longitude"]].to_numpy().tolist()

FastMarkerCluster(points).add_to(nyc_map)

st_folium(nyc_map, width=700)

st.subheader("NYC Evictions 2017-Present by Count")

borough_count_clean = borough_count(eviction_data)
st.bar_chart(borough_count_clean, x="borough", y="Count", x_label="NYC Borough", y_label="Total")

st.divider()


@contextmanager
def display_load_time():
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        st.caption(f"Page loaded in {elapsed:.2f} seconds")
