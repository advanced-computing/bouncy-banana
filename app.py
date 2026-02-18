import streamlit as st
import pandas as pd
import requests
from fred import fetch_fred
from eviction import eviction, borough_count

fred_key = "aa9cd57aae80525dc171dbc517b39546"

claims_df = fetch_fred("NYICLAIMS",fred_key,"Claims")

#Claims
st.line_chart(claims_df, x = "Date", y = "Claims")

continued_claims_df = fetch_fred("NYCCLAIMS", fred_key,"Continued Claims")

#Continued Claims
st.line_chart(continued_claims_df, x = "Date", y ="Continued Claims")

############################################################################################

# Evictions Dataset
eviction_df = eviction()
# Eviction Count in Boroughs
borough_data = borough_count(eviction_df)
st.bar_chart(borough_data, x = "borough", y = "Count")


#streamlit run app.py