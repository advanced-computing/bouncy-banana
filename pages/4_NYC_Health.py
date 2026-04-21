import time
from contextlib import contextmanager

# import numpy as np
import pandas as pd

# import plotly.express as px
# import plotly.graph_objects as go
import streamlit as st

# from google.cloud import bigquery
# from plotly.subplots import make_subplots
from fred_data import fred_from_bigquery
from health_bq import health
from utils.styles import apply_global_styles

# configure browser tab
st.set_page_config(
    page_title="NYC Health & Unemployment",
    page_icon="🗽",
    layout="wide",
)

apply_global_styles()


# cache health data
@st.cache_data
def load_health_bq():
    return health()


@st.cache_data
def load_fred_data():
    return fred_from_bigquery()


@contextmanager
def display_load_time():
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        st.caption(f"Page loaded in {elapsed:.2f} seconds")


with display_load_time():
    # load cached data
    health_data = load_health_bq()
    fred_data = load_fred_data()

    # change weekly insurance claims to yearly to match health data
    fred_data["year"] = pd.to_datetime(fred_data["Date"]).dt.year
    fred_yearly = fred_data.groupby("year")["Claims"].sum().reset_index()

    # merge on year
    merged = health_data.merge(fred_yearly, on="year", how="inner")

    # make sidebar filter for year
    st.sidebar.header("Filters")

    years = sorted(health_data["year"].unique().tolist())
    selected_years = st.sidebar.multiselect("Year", years, default=years)

    # add clear option to button
    if st.sidebar.button("Clear Years"):
        selected_years = years

    # apply the filter
    filtered = health_data[health_data["year"].isin(selected_years)]

    st.title("NYC Health Data")

    # summary metrics
    st.subheader("Key Insights")

    # Use filtered year if you have a sidebar filter, otherwise latest year
    latest_year = merged["year"].max()
    latest = merged[merged["year"] == latest_year].iloc[0]

    # Peak unemployment year
    peak_year = fred_yearly.loc[fred_yearly["Claims"].idxmax(), "year"]
    peak_uninsured = merged[merged["year"] == peak_year]["No Health Insurance"].to_numpy()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Unemployment Claims",
            value=f"{int(latest['Claims']):,}",
            delta=f"{latest_year}",
        )

    with col2:
        st.metric(
            label="Uninsured Rate",
            value=f"{latest['No Health Insurance']}%",
            delta=f"{latest_year}",
        )

    with col3:
        if len(peak_uninsured) > 0:
            st.metric(
                label="Peak Unemployment Year",
                value=f"{int(peak_year)}",
                delta=f"{peak_uninsured[0]}% uninsured that year",
            )
    st.divider()
