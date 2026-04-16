import time
from contextlib import contextmanager

import pandas as pd

# import pydata_google_auth
import streamlit as st
from google.oauth2 import service_account

from fred import fred_from_bigquery

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
            background-color:#CAE7D3;
            padding:20px;
            border-radius:8px;
            border-left:6px solid #2E6F40;
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
