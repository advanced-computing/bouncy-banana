import streamlit as st

from fred import fetch_fred

fred_key = "aa9cd57aae80525dc171dbc517b39546"
claims_df = fetch_fred("NYICLAIMS", fred_key, "Claims")

st.title("Exploring Unemployment in New York City")
st.subheader("Advanced Computing for Policy, Spring 2026 | Sophia Cain and Samuel Fu")

st.divider()

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
        This project explores unemployment trends in New York City using data from FRED.
        We analyze both initial unemployment claims and continued claims over time
        to understand how economic shocks affect the labor market.
    </div>
    """,
    unsafe_allow_html=True,
)

st.header("Unemployment Claims in New York City OVer Time")
st.line_chart(claims_df, x="Date", y="Claims")

continued_claims_df = fetch_fred("NYCCLAIMS", fred_key, "Continued Claims")
st.header("Continued Unemployment Claims in New York City Over Time")
st.line_chart(continued_claims_df.set_index("Date")["Continued Claims"])
