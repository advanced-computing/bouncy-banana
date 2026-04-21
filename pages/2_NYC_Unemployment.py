import time
from contextlib import contextmanager

import pandas as pd
import streamlit as st
from google.oauth2 import service_account

from fred_data import fred_from_bigquery
from utils.styles import apply_global_styles

apply_global_styles()

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# configure browser tab
st.set_page_config(
    page_title="NYC Unemployment Dashboard",
    page_icon="🗽",
    layout="wide",
)

apply_global_styles()


# cache unemployment data
@st.cache_data
def load_fred_data():
    return fred_from_bigquery(credentials, "new_insurance")


@st.cache_data
def load_fred_continued_data():
    return fred_from_bigquery(credentials, "continued_insurance_table")


# set up page load time
@contextmanager
def display_load_time():
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        st.caption(f"Page loaded in {elapsed:.2f} seconds")


with display_load_time():
    fred_key = "aa9cd57aae80525dc171dbc517b39546"
    claims_df = fred_from_bigquery(credentials, "new_insurance_table")
    claims_df["Date"] = pd.to_datetime(claims_df["Date"])

    # load cached data
    fred_data_cache = load_fred_data()

    # change weekly insurance claims to yearly
    fred_data_cache["year"] = pd.to_datetime(fred_data_cache["Date"]).dt.year
    fred_yearly = fred_data_cache.groupby("year")["Claims"].sum().reset_index()

    # find peak unemployment year
    peak_year = int(fred_yearly.loc[fred_yearly["Claims"].idxmax(), "year"])
    peak_claims = int(fred_yearly.loc[fred_yearly["Claims"].idxmax(), "Claims"])

    st.title("NYC Unemployment Data")

    # summary metrics
    st.subheader("Key Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Peak Unemployment Year",
            value=f"{peak_year}",
            delta=f"{peak_claims:,} claims",
        )

    with col2:
        latest_year = int(fred_yearly["year"].max())
        latest_claims = int(fred_yearly.loc[fred_yearly["year"].idxmax(), "Claims"])
        st.metric(
            label="Latest Year Claims",
            value=f"{latest_year}",
            delta=f"{latest_claims:,} claims",
        )

    with col3:
        avg_claims = int(fred_yearly["Claims"].mean())
        st.metric(
            label="Average Annual Claims",
            value=f"{avg_claims:,}",
            delta="all years",
        )
    st.divider()

    st.header("Unemployment Claims in New York City")
    st.text("NYC Open Data")
    st.markdown(
        """
        <div style="
            background-color:#E5F3FD;
            padding:20px;
            border-radius:8px;
            border-left:6px solid #9ABDDC;
            font-size:17px;
        ">
            This graph shows overall total unemployment claims made
            in NYC from 1986 to 2019 across the
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

    continued_claims_df = fred_from_bigquery(credentials, "continued_insurance_table")
    continued_claims_df["Date"] = pd.to_datetime(continued_claims_df["Date"])
    st.header("Continued Unemployment Claims in New York City")
    st.text("NYC Open Data")
    st.markdown(
        """
        <div style="
            background-color:#E5F3FD;
            padding:20px;
            border-radius:8px;
            border-left:6px solid #9ABDDC;
            font-size:17px;
        ">
            This graph shows overall total continued unemployment claims
            (claims made after the inital
            unemployment filing made in NYC from
            1986 to 2019 across the five boroughs.
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

    st.line_chart(filtered_continued, x="Date", y="Claims")

    st.divider()
