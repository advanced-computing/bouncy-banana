import time
from contextlib import contextmanager

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from folium.plugins import FastMarkerCluster
from google.oauth2 import service_account
from streamlit_folium import st_folium

from eviction import borough_count, eviction
from fred import fred_from_bigquery
from utils.styles import apply_global_styles

apply_global_styles()

# SCOPES = [
#     "https://www.googleapis.com/auth/cloud-platform",
#     "https://www.googleapis.com/auth/drive",
# ]

# credentials = pydata_google_auth.get_user_credentials(
#     SCOPES,
#     auth_local_webserver=True,
# )

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)


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
st.bar_chart(
    borough_count_clean,
    x="borough",
    y="Count",
    color="#0f0f59",
    x_label="NYC Borough",
    y_label="Total",
)

st.divider()

st.subheader("Evictions vs Unemployment Claims in NYC")

boroughs = ["All"] + list(eviction_data["borough"].unique())
selected_borough = st.selectbox("Filter by Borough", boroughs)

if selected_borough != "All":
    filtered_evictions = eviction_data[eviction_data["borough"] == selected_borough]
else:
    filtered_evictions = eviction_data

# Aggregate evictions by date (assuming eviction_data has a date column)
eviction_data["year"] = pd.to_datetime(eviction_data["executed_date"]).dt.year
evictions_by_year = eviction_data.groupby("year").size().reset_index(name="Evictions")

claims_df = fred_from_bigquery(credentials, "new_insurance_table")
claims_df["Date"] = pd.to_datetime(claims_df["Date"])

# Aggregate claims by year
claims_df["year"] = claims_df["Date"].dt.year
claims_by_year = claims_df.groupby("year")["Claims"].sum().reset_index()

# Merge on year
merged = evictions_by_year.merge(claims_by_year, on="year")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=merged["year"],
        y=merged["Evictions"],
        name="Evictions",
        marker_color="#0f0f59",
        yaxis="y1",
    )
)

fig.add_trace(
    go.Scatter(
        x=merged["year"],
        y=merged["Claims"],
        name="Unemployment Claims",
        line=dict(color="#93b9e1", width=3),
        yaxis="y2",
    )
)

fig.update_layout(
    xaxis=dict(title="Year"),
    yaxis=dict(title="Evictions", side="left"),
    yaxis2=dict(title="Unemployment Claims", side="right", overlaying="y"),
    legend=dict(x=0.01, y=0.99),
    plot_bgcolor="#ffffff",
    hovermode="x unified",  # shows both values on hover
)

st.plotly_chart(fig, use_container_width=True)


@contextmanager
def display_load_time():
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        st.caption(f"Page loaded in {elapsed:.2f} seconds")
