import base64
import time
from contextlib import contextmanager

import pandas as pd
import streamlit as st

from fred_data import fetch_fred
from utils.styles import apply_global_styles

# set_page_config must be the first Streamlit call
st.set_page_config(
    page_title="Project Documentation",
    page_icon="🗽",
    layout="wide",
)

apply_global_styles()


@contextmanager
def display_load_time():
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        st.caption(f"Page loaded in {elapsed:.2f} seconds")


def nyc_skyline_banner():
    svg = """
    <svg viewBox="0 0 900 160" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;">
      <rect x="0"   y="100" width="40"  height="60" fill="#112244"/>
      <rect x="30"  y="80"  width="25"  height="80" fill="#0e1e3d"/>
      <rect x="50"  y="90"  width="35"  height="70" fill="#112244"/>
      <rect x="80"  y="70"  width="20"  height="90" fill="#0e1e3d"/>
      <rect x="95"  y="85"  width="30"  height="75" fill="#112244"/>
      <rect x="130" y="40"  width="30"  height="120" fill="#1a3060"/>
      <rect x="138" y="20"  width="14"  height="30"  fill="#1a3060"/>
      <rect x="143" y="5"   width="4"   height="20"  fill="#1a3060"/>
      <rect x="175" y="55"  width="25"  height="105" fill="#112244"/>
      <polygon points="175,55 187,25 200,55" fill="#1a3060"/>
      <rect x="200" y="75"  width="40"  height="85"  fill="#0e1e3d"/>
      <rect x="235" y="60"  width="20"  height="100" fill="#112244"/>
      <rect x="250" y="80"  width="35"  height="80"  fill="#1a2f5e"/>
      <rect x="280" y="65"  width="25"  height="95"  fill="#0e1e3d"/>
      <polygon points="310,10 330,75 350,75 370,10" fill="#1a3060" opacity="0.9"/>
      <rect x="315" y="75"  width="50"  height="85"  fill="#1a3060"/>
      <rect x="370" y="70"  width="30"  height="90"  fill="#112244"/>
      <rect x="395" y="50"  width="20"  height="110" fill="#0e1e3d"/>
      <rect x="410" y="80"  width="40"  height="80"  fill="#1a2f5e"/>
      <rect x="445" y="60"  width="25"  height="100" fill="#112244"/>
      <rect x="465" y="75"  width="35"  height="85"  fill="#0e1e3d"/>
      <rect x="495" y="55"  width="22"  height="105" fill="#1a3060"/>
      <rect x="512" y="80"  width="40"  height="80"  fill="#112244"/>
      <rect x="548" y="65"  width="28"  height="95"  fill="#0e1e3d"/>
      <rect x="572" y="85"  width="35"  height="75"  fill="#1a2f5e"/>
      <rect x="603" y="70"  width="20"  height="90"  fill="#112244"/>
      <rect x="618" y="50"  width="30"  height="110" fill="#0e1e3d"/>
      <rect x="645" y="75"  width="40"  height="85"  fill="#1a3060"/>
      <rect x="680" y="60"  width="25"  height="100" fill="#112244"/>
      <rect x="700" y="80"  width="35"  height="80"  fill="#0e1e3d"/>
      <rect x="730" y="65"  width="22"  height="95"  fill="#1a2f5e"/>
      <rect x="748" y="85"  width="40"  height="75"  fill="#112244"/>
      <rect x="784" y="70"  width="28"  height="90"  fill="#0e1e3d"/>
      <rect x="808" y="55"  width="20"  height="105" fill="#1a3060"/>
      <rect x="824" y="80"  width="40"  height="80"  fill="#112244"/>
      <rect x="860" y="65"  width="30"  height="95"  fill="#0e1e3d"/>
      <rect x="133" y="50"  width="4" height="3" fill="#f4c27a" opacity="0.7"/>
      <rect x="141" y="65"  width="4" height="3" fill="#f4c27a" opacity="0.6"/>
      <rect x="133" y="80"  width="4" height="3" fill="#f4c27a" opacity="0.8"/>
      <rect x="141" y="95"  width="4" height="3" fill="#f4c27a" opacity="0.5"/>
      <rect x="316" y="85"  width="5" height="3" fill="#f4c27a" opacity="0.7"/>
      <rect x="326" y="100" width="5" height="3" fill="#f4c27a" opacity="0.6"/>
      <rect x="336" y="85"  width="5" height="3" fill="#f4c27a" opacity="0.8"/>
      <rect x="204" y="85"  width="4" height="3" fill="#f4c27a" opacity="0.6"/>
      <rect x="212" y="100" width="4" height="3" fill="#f4c27a" opacity="0.7"/>
      <rect x="500" y="65"  width="4" height="3" fill="#f4c27a" opacity="0.6"/>
      <rect x="500" y="80"  width="4" height="3" fill="#f4c27a" opacity="0.8"/>
      <rect x="622" y="60"  width="4" height="3" fill="#f4c27a" opacity="0.7"/>
      <rect x="622" y="75"  width="4" height="3" fill="#f4c27a" opacity="0.5"/>
    </svg>
    """

    b64 = base64.b64encode(svg.encode()).decode()

    st.markdown(
        f"""
        <div style="
            width: 100%;
            background: linear-gradient(180deg, #0a1628 0%, #1a2f5e 40%, #e8925a 75%, #f4c27a 100%);
            border-radius: 12px;
            padding: 24px 0px 0px 0px;
            margin-bottom: 28px;
            overflow: hidden;
            position: relative;
        ">
            <!-- Stars -->
            <div style="position:absolute;top:10px;left:8%;width:2px;height:2px;background:white;
            border-radius:50%;opacity:0.9;"></div>
            <div style="position:absolute;top:18px;left:22%;width:1px;height:1px;background:white;
            border-radius:50%;opacity:0.7;"></div>
            <div style="position:absolute;top:8px;left:35%;width:2px;height:2px;background:white;
            border-radius:50%;opacity:0.8;"></div>
            <div style="position:absolute;top:22px;left:50%;width:1px;height:1px;background:white;
            border-radius:50%;opacity:0.6;"></div>
            <div style="position:absolute;top:12px;left:65%;width:2px;height:2px;background:white;
            border-radius:50%;opacity:0.9;"></div>
            <div style="position:absolute;top:6px;left:80%;width:1px;height:1px;background:white;
            border-radius:50%;opacity:0.7;"></div>
            <div style="position:absolute;top:20px;left:90%;width:2px;height:2px;background:white;
            border-radius:50%;opacity:0.8;"></div>
            <div style="position:absolute;top:14px;right:12%;width:22px;height:22px;
            background:#f5e6a3;border-radius:50%;box-shadow:0 0 12px #f5e6a3aa;"></div>
            <img src="data:image/svg+xml;base64,{b64}" style="width:100%;display:block;"/>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dataset_cards():
    datasets = [
        {
            "icon": "📈",
            "name": "FRED Unemployment Insurance Claims",
            "source": "Federal Reserve Economic Data (FRED)",
            "description": "Weekly initial and continued unemployment insurance claims"
            " filed in New York State,"
            " sourced from the St. Louis Fed.",
            "color": "#1a3060",
        },
        {
            "icon": "🏠",
            "name": "Eviction Records",
            "source": "NYC Open Data",
            "description": "Eviction filings, shelter census, and housing court data tracking "
            "housing instability across NYC boroughs.",
            "color": "#1a3060",
        },
        {
            "icon": "🏥",
            "name": "Public Health Indicators",
            "source": "NYC Open Data",
            "description": "Community health survey data covering different health indicators"
            " and access to care over time.",
            "color": "#1a3060",
        },
    ]

    cols = st.columns(len(datasets))
    for col, ds in zip(cols, datasets, strict=True):
        with col:
            st.markdown(
                f"""
                <div style="
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    border-top: 5px solid {ds["color"]};
                    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                    height: 100%;
                ">
                    <div style="font-size:28px; margin-bottom:8px;">{ds["icon"]}</div>
                    <div style="font-weight:700; font-size:15px; color:#0e1e3d;
                      margin-bottom:4px;">{ds["name"]}</div>
                    <div style="font-size:12px; color:#6b7a99; margin-bottom:10px;
                      font-style:italic;">{ds["source"]}</div>
                    <div style="font-size:14px; color:#333;
                      line-height:1.5;">{ds["description"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


with display_load_time():
    fred_key = "aa9cd57aae80525dc171dbc517b39546"
    claims_df = fetch_fred("NYICLAIMS", fred_key, "Claims")
    claims_df["Date"] = pd.to_datetime(claims_df["Date"])

    # skyline banner
    nyc_skyline_banner()

    st.title("Project Proposal: Exploring Unemployment and Lifestyle Metrics in NYC")
    st.text("Advanced Computing for Policy, Spring 2026 | Sophia Cain and Samuel Fu")

    st.divider()

    # project overview
    st.subheader("Project Overview")
    st.markdown(
        """
        <div style="
            background-color:#E5F3FD;
            padding:20px;
            border-radius:8px;
            border-left:6px solid #9ABDDC;
            font-size:17px;
        ">
            This project examines how unemployment trends intersect with key lifestyle
            metrics — including housing security and public health — for New Yorkers
            over time. We offer a comprehensive dashboard providing a high-level view
            of all variables, alongside dedicated pages for deeper dives into each topic.
            Interactive elements allow users to explore and analyze these trends
            across different time periods.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # dataset cards
    st.subheader("Datasets")
    dataset_cards()

    st.divider()

    # borough photo
    st.subheader("Geographic Context")
    st.caption("Image courtsey of Loumovesyou.com")
    st.caption("Unemployment data in this project is scoped to the five boroughs of New York City.")
    st.markdown(
        """
    <div style="text-align: center;">
        <img src="https://www.loumovesyou.com/wp-content/uploads/2022/11/FiveBoroughs-01.jpg"
          style="width: 50%;"/>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.divider()
