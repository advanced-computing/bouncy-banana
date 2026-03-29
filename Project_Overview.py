import pandas as pd
import streamlit as st

from fred import fetch_fred

fred_key = "aa9cd57aae80525dc171dbc517b39546"
claims_df = fetch_fred("NYICLAIMS", fred_key, "Claims")
claims_df["Date"] = pd.to_datetime(claims_df["Date"])

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
