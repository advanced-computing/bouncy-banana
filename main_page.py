import streamlit as st

from fred import fetch_fred

fred_key = "aa9cd57aae80525dc171dbc517b39546"
claims_df = fetch_fred("NYICLAIMS", fred_key, "Claims")

st.title("Exploring Unemployment in New York City")
st.subheader("Advanced Computing for Policy, Spring 2026 | Sophia Cain and Samuel Fu")

st.divider()

st.header("Project Proposal")
st.markdown("test", unsafe_allow_html=False, *, help=None, width="auto", 
            text_alignment="left", background="CAE7D3")

st.header("Unemployment Claims in New York City OVer Time")
st.line_chart(claims_df, x="Date", y="Claims")

continued_claims_df = fetch_fred("NYCCLAIMS", fred_key, "Continued Claims")
st.header("Continued Unemployment Claims in New York City Over Time")
st.line_chart(continued_claims_df.set_index("Date")["Continued Claims"])