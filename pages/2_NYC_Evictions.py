import time
from contextlib import contextmanager

import folium
import streamlit as st
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium

from eviction import borough_count, eviction


@st.cache_data(ttl=3600)
def load_eviction_data():
    df = eviction()
    df = df.dropna(subset=["latitude", "longitude"])
    return df


eviction_data = load_eviction_data()

nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

points = eviction_data[["latitude", "longitude"]].to_numpy().tolist()

nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)
FastMarkerCluster(points).add_to(nyc_map)

st.title("NYC Eviction Data")
st_folium(nyc_map, width=700)

borough_count_clean = borough_count(eviction_data)
st.bar_chart(borough_count_clean, x="borough", y="Count")


@contextmanager
def display_load_time():
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        st.caption(f"Page loaded in {elapsed:.2f} seconds")
