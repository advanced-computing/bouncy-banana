import time
from contextlib import contextmanager

import pandas as pd
import streamlit as st

from fred_data import fetch_fred
from utils.styles import apply_global_styles

apply_global_styles()

# configure browser tab
st.set_page_config(
    page_title="Project Documentation",
    page_icon="🗽",
    layout="wide",
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
    claims_df = fetch_fred("NYICLAIMS", fred_key, "Claims")
    claims_df["Date"] = pd.to_datetime(claims_df["Date"])

    st.title("Exploring Unemployment in New York City")
    st.text("Advanced Computing for Policy, Spring 2026 | Sophia Cain and Samuel Fu")

    st.divider()

    st.subheader("Project Proposal")
    st.markdown(
        """
        <div style="
            background-color:#E5F3FD;
            padding:20px;
            border-radius:8px;
            border-left:6px solid #9ABDDC;
            font-size:17px;
        ">
            This project explores unemployment trends in
            New York City using data from  Federal Reserve
            Economic Data (FRED) and NYC Open Data.
            We analyze both initial unemployment claims and
            continued claims over time to understand how
            unemployment effects New Yorkers in the short-
            and long-term. We are introducing more
            data from NYC Open Data to explore the relationship
            between unemployment and health.
            We will also introduce a geographical component to this
            data in the coming weeks. Stay tuned for updates!
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
