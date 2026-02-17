import streamlit as st
import pandas as pd
import requests
from fred import fetch_fred

fred_key = "aa9cd57aae80525dc171dbc517b39546"

claims_df = fetch_fred("NYICLAIMS",fred_key,"Claims")

#Claims
st.line_chart(claims_df.set_index("Date")["Claims"])

continued_claims_df = fetch_fred("NYCCLAIMS", fred_key,"Continued Claims")

#Continued Claims
st.line_chart(continued_claims_df.set_index("Date")["Continued Claims"])

#streamlit run app.py