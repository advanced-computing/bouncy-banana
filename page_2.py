import folium
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from eviction import borough_count, eviction

eviction_data = eviction()
eviction_data = eviction_data.dropna(subset=["latitude", "longitude"])

borough_count_clean = borough_count(eviction_data)

st.bar_chart(borough_count_clean, x="borough", y="Count")

nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

marker_cluster = MarkerCluster().add_to(nyc_map)
for _i, r in eviction_data.iterrows():
    folium.Marker(
        location=[r["latitude"],
                  r["longitude"]],
                  popup=r["eviction_address"],
                  tooltip="Eviction"
    ).add_to(marker_cluster)

st.title("NYC Eviction Data")
st.sidebar.markdown("Page 2")

st_folium(nyc_map, width=700)
