import pandas as pd
import streamlit as st

from fred import fetch_fred

fred_key = "aa9cd57aae80525dc171dbc517b39546"
claims_df = fetch_fred("NYICLAIMS", fred_key, "Claims")
claims_df["Date"] = pd.to_datetime(claims_df["Date"]).dt.date

st.title("Exploring Unemployment in New York City")
st.text("Advanced Computing for Policy, Spring 2026 | Sophia Cain and Samuel Fu")

st.divider()

st.badge("New")
st.header("Project Proposal")
st.markdown(
    """
    <div style="
        background-color:#CAE7D3;
        padding:20px;
        border-radius:8px;
        border-left:6px solid #2E6F40;
        font-size:17px;
    ">
        This project explores unemployment trends in New York City using data from  Federal Reserve
         Economic Data (FRED) and NYC Open Data. We analyze both initial unemployment claims and
         continued claims over time to understand how unemployment effects New Yorkers in the short-
          and long-term. We are introducing more data from NYC Open Data to explore the relationship
          between unemployment and health. We will also introduce a geographical component to this
          data in the coming weeks. Stay tuned for updates!
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

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
    min_value=claims_df["Date"].min(),
    max_value=claims_df["Date"].max(),
    value=(claims_df["Date"].min(), claims_df["Date"].max()),
)

filtered_claims = claims_df[(claims_df["Date"] >= start_date) & (claims_df["Date"] <= end_date)]
st.line_chart(filtered_claims, x="Date", y="Claims")

st.divider()

continued_claims_df = fetch_fred("NYCCLAIMS", fred_key, "Continued Claims")
continued_claims_df["Date"] = pd.to_datetime(continued_claims_df["Date"]).dt.date
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
    min_value=continued_claims_df["Date"].min(),
    max_value=continued_claims_df["Date"].max(),
    value=(continued_claims_df["Date"].min(), continued_claims_df["Date"].max()),
)

filtered_continued = continued_claims_df[
    (continued_claims_df["Date"] >= start_date2) & (continued_claims_df["Date"] <= end_date2)
]

st.line_chart(filtered_continued, x="Date", y="Continued Claims")
