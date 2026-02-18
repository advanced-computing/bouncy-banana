import pandas as pd
import requests
import streamlit as st

from fred import fetch_fred

fred_key = "aa9cd57aae80525dc171dbc517b39546"

claims_df = fetch_fred("NYICLAIMS", fred_key, "Claims")

main_page = st.Page("main_page.py", title="Main Page")
page_2 = st.Page("page_2.py", title="Page 2")

pg = st.navigation([main_page, page_2])

st.markdown("# Main page")
st.sidebar.markdown("# Main page")

# Claims
st.line_chart(claims_df.set_index("Date")["Claims"])

continued_claims_df = fetch_fred("NYCCLAIMS", fred_key, "Continued Claims")

st.markdown("# Page 2")
st.sidebar.markdown("# Page 2")

# Continued Claims
st.line_chart(continued_claims_df.set_index("Date")["Continued Claims"])

# streamlit run app.py
