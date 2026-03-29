import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from eviction import borough_count, eviction
from fred import fetch_fred

fred_key = "aa9cd57aae80525dc171dbc517b39546"
claims_df = fetch_fred("NYICLAIMS", fred_key, "Claims")
claims_df["Date"] = pd.to_datetime(claims_df["Date"])

st.header("Unemployment Claims in New York City")
st.text("NYC Open Data")
st.markdown(
    """
    <div style="
        background-color:#CAE7D3;
        padding:20px;
        border-radius:8px;
        border-left:6px solid #2E6F40;
        font-size:17px;
    ">
        This graph shows overall total unemployment claims made in NYC from 1986 to 2019 across the
         five boroughs.
    </div>
    """,
    unsafe_allow_html=True,
)


start_date, end_date = st.slider(
    "Select Date Range",
    min_value=claims_df["Date"].min().to_pydatetime(),
    max_value=claims_df["Date"].max().to_pydatetime(),
    value=(claims_df["Date"].min().to_pydatetime(), claims_df["Date"].max().to_pydatetime()),
)

filtered_claims = claims_df[(claims_df["Date"] >= start_date) & (claims_df["Date"] <= end_date)]
st.line_chart(filtered_claims, x="Date", y="Claims")

st.divider()

continued_claims_df = fetch_fred("NYCCLAIMS", fred_key, "Continued Claims")
continued_claims_df["Date"] = pd.to_datetime(continued_claims_df["Date"])
st.header("Continued Unemployment Claims in New York City")
st.text("NYC Open Data")
st.markdown(
    """
    <div style="
        background-color:#CAE7D3;
        padding:20px;
        border-radius:8px;
        border-left:6px solid #2E6F40;
        font-size:17px;
    ">
        This graph shows overall total continued unemployment claims (claims made after the inital
         unemployment filing made in NYC from 1986 to 2019 across the five boroughs.
    </div>
    """,
    unsafe_allow_html=True,
)


start_date2, end_date2 = st.slider(
    "Select Date Range for Continued Claims",
    min_value=continued_claims_df["Date"].min().to_pydatetime(),
    max_value=continued_claims_df["Date"].max().to_pydatetime(),
    value=(
        continued_claims_df["Date"].min().to_pydatetime(),
        continued_claims_df["Date"].max().to_pydatetime(),
    ),
)

filtered_continued = continued_claims_df[
    (continued_claims_df["Date"] >= start_date2) & (continued_claims_df["Date"] <= end_date2)
]

st.line_chart(filtered_continued, x="Date", y="Continued Claims")

st.divider()

eviction_data = eviction()
eviction_data = eviction_data.dropna(subset=["latitude", "longitude"])

nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

marker_cluster = MarkerCluster().add_to(nyc_map)
for _i, r in eviction_data.iterrows():
    folium.Marker(
        location=[r["latitude"], r["longitude"]], popup=r["eviction_address"], tooltip="Eviction"
    ).add_to(marker_cluster)

st.title("NYC Eviction Data")

st_folium(nyc_map, width=700)

borough_count_clean = borough_count(eviction_data)


st.bar_chart(borough_count_clean, x="borough", y="Count")
