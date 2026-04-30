import time
from contextlib import contextmanager

import pandas as pd
import plotly.express as px
import streamlit as st
from google.oauth2 import service_account

from src.functions.fred_data import fetch_fred, fred_from_bigquery
from src.utils.styles import apply_global_styles

# apply universal formatting
apply_global_styles()

# bq credentials
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# format page tab
st.set_page_config(
    page_title="NYC Unemployment Dashboard",
    page_icon="🗽",
    layout="wide",
)

FRED_KEY = "aa9cd57aae80525dc171dbc517b39546"
RATE_LABEL = "Unemployment Rate (%)"


# load cached data frames
@st.cache_data
def load_fred_new_claims():
    return fred_from_bigquery(credentials, "new_insurance_table")


@st.cache_data
def load_fred_continued_claims():
    return fred_from_bigquery(credentials, "continued_insurance_table")


@st.cache_data
def load_ny_unemployment_rate():
    df = fetch_fred("NYUR", FRED_KEY, RATE_LABEL, frequency="m")
    df = df.sort_values("Date").reset_index(drop=True)
    for months in [1, 3, 6, 12]:
        df[f"{months}-Month Net Change"] = df[RATE_LABEL].diff(months).round(2)
        df[f"{months}-Month % Change"] = (df[RATE_LABEL].pct_change(months) * 100).round(1)
    return df


# page formatting
@contextmanager
def display_load_time():
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        st.caption(f"Page loaded in {elapsed:.2f} seconds")


def info_box(text: str):
    st.markdown(
        f"""
        <div style="
            background-color:#E5F3FD;
            padding:20px;
            border-radius:8px;
            border-left:6px solid #9ABDDC;
            font-size:17px;
        ">{text}</div>
        """,
        unsafe_allow_html=True,
    )


def aggregate_monthly(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    df = df.copy()
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    return df.groupby("Month")[value_col].sum().reset_index().rename(columns={"Month": "Date"})


with display_load_time():
    claims_df = load_fred_new_claims()
    claims_df["Date"] = pd.to_datetime(claims_df["Date"])

    continued_df = load_fred_continued_claims()
    continued_df["Date"] = pd.to_datetime(continued_df["Date"])

    # aggregate yearly for key metrics
    claims_df_yearly = claims_df.copy()
    claims_df_yearly["year"] = claims_df_yearly["Date"].dt.year
    fred_yearly = claims_df_yearly.groupby("year")["Claims"].sum().reset_index()

    peak_year = int(fred_yearly.loc[fred_yearly["Claims"].idxmax(), "year"])
    peak_claims = int(fred_yearly.loc[fred_yearly["Claims"].idxmax(), "Claims"])

    st.title("NYC Unemployment Dashboard")

    # key metrics
    st.subheader("Key Insights")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Peak Unemployment Year", f"{peak_year}", f"{peak_claims:,} claims")
    with col2:
        latest_year = int(fred_yearly["year"].max())
        latest_claims = int(fred_yearly.loc[fred_yearly["year"].idxmax(), "Claims"])
        st.metric("Latest Year Claims", f"{latest_year}", f"{latest_claims:,} claims")
    with col3:
        avg_claims = int(fred_yearly["Claims"].mean())
        st.metric("Average Annual Claims", f"{avg_claims:,}", "all years")

    st.divider()

    # BLS Unemployment Rate
    month_check = 13
    st.header("BLS Unemployment Rate — New York State")
    st.caption(
        "Source: U.S. Bureau of Labor Statistics — Local Area Unemployment Statistics "
        "(New York State)"
    )

    try:
        bls_df = load_ny_unemployment_rate()

        latest_rate = float(bls_df[RATE_LABEL].iloc[-1])
        prev_year_rate = float(bls_df[RATE_LABEL].iloc[-13]) if len(bls_df) > month_check else None
        yoy_delta = round(latest_rate - prev_year_rate, 1) if prev_year_rate is not None else None

        b1, b2, b3 = st.columns(3)
        with b1:
            st.metric(
                "Current Unemployment Rate",
                f"{latest_rate:.1f}%",
                delta=f"{yoy_delta:+.1f}pp YoY" if yoy_delta is not None else None,
                delta_color="inverse",
            )
        with b2:
            peak_bls = bls_df.loc[bls_df[RATE_LABEL].idxmax()]
            st.metric(
                "Peak Rate",
                f"{peak_bls[RATE_LABEL]:.1f}%",
                f"{peak_bls['Date'].strftime('%b %Y')}",
            )
        with b3:
            min_bls = bls_df.loc[bls_df[RATE_LABEL].idxmin()]
            st.metric(
                "Lowest Rate",
                f"{min_bls[RATE_LABEL]:.1f}%",
                f"{min_bls['Date'].strftime('%b %Y')}",
            )

        info_box(
            "Monthly unemployment rate (%) for New York State from the Bureau of Labor "
            "Statistics Local Area Unemployment Statistics (LAUS) program. State-level "
            "unemployment closely tracks NYC trends and is used here as the BLS benchmark."
        )

        bls_start, bls_end = st.slider(
            "Select Date Range (BLS)",
            min_value=bls_df["Date"].min().to_pydatetime(),
            max_value=bls_df["Date"].max().to_pydatetime(),
            value=(bls_df["Date"].min().to_pydatetime(), bls_df["Date"].max().to_pydatetime()),
            key="bls_slider",
        )
        filtered_bls = bls_df[(bls_df["Date"] >= bls_start) & (bls_df["Date"] <= bls_end)]

        st.line_chart(filtered_bls, x="Date", y=RATE_LABEL)

        with st.expander("Month-over-Month & Year-over-Year Changes"):
            change_cols = [
                "Date",
                RATE_LABEL,
                "1-Month Net Change",
                "3-Month Net Change",
                "12-Month Net Change",
                "12-Month % Change",
            ]
            display_cols = [c for c in change_cols if c in bls_df.columns]
            st.dataframe(
                filtered_bls[display_cols]
                .sort_values("Date", ascending=False)
                .reset_index(drop=True),
                use_container_width=True,
            )

    except Exception as e:
        st.warning(str(e))
        bls_df = None

    st.divider()

    # New Unemployment Claims
    st.header("New Unemployment Claims — New York City")
    st.text("Source: NYC Open Data")
    info_box(
        "Weekly new (initial) unemployment insurance claims filed in NYC from 1986 to 2019 "
        "across the five boroughs."
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

    # Continued Unemployment Claims
    st.header("Continued Unemployment Claims — New York City")
    st.text("Source: NYC Open Data")
    info_box(
        "Weekly continued unemployment claims (filed after the initial claim) in NYC from "
        "1986 to 2019 across the five boroughs."
    )

    start_date2, end_date2 = st.slider(
        "Select Date Range for Continued Claims",
        min_value=continued_df["Date"].min().to_pydatetime(),
        max_value=continued_df["Date"].max().to_pydatetime(),
        value=(
            continued_df["Date"].min().to_pydatetime(),
            continued_df["Date"].max().to_pydatetime(),
        ),
    )
    filtered_continued = continued_df[
        (continued_df["Date"] >= start_date2) & (continued_df["Date"] <= end_date2)
    ]
    st.line_chart(filtered_continued, x="Date", y="Claims")

    st.divider()

    # Correlation & Analysis
    st.header("BLS Unemployment Rate vs. Claims")

    if bls_df is not None:
        info_box(
            "Monthly BLS unemployment rate compared against monthly-aggregated new and "
            "continued unemployment claims. Correlation and scatter plots show "
            "how closely claims track the official unemployment rate."
        )

        # aggregate weekly claims on monthly totals
        new_monthly = aggregate_monthly(claims_df, "Claims").rename(
            columns={"Claims": "New Claims"}
        )
        cont_monthly = aggregate_monthly(continued_df, "Claims").rename(
            columns={"Claims": "Continued Claims"}
        )

        # align BLS to monthly period (already monthly)
        bls_monthly = bls_df[["Date", RATE_LABEL]].copy()
        bls_monthly["Date"] = bls_monthly["Date"].dt.to_period("M").dt.to_timestamp()

        # merge
        merged = bls_monthly.merge(new_monthly, on="Date", how="inner")
        merged = merged.merge(cont_monthly, on="Date", how="inner")

        corr_new = merged[RATE_LABEL].corr(merged["New Claims"])
        corr_cont = merged[RATE_LABEL].corr(merged["Continued Claims"])

        c1, c2 = st.columns(2)
        with c1:
            st.metric(
                "Correlation: Rate vs. New Claims",
                f"{corr_new:.3f}",
                help="r — values near ±1 indicate a strong linear relationship",
            )
        with c2:
            st.metric(
                "Correlation: Rate vs. Continued Claims",
                f"{corr_cont:.3f}",
                help="r — values near ±1 indicate a strong linear relationship",
            )

        st.subheader("Scatter Plots")
        sc1, sc2 = st.columns(2)

        with sc1:
            fig_new = px.scatter(
                merged,
                x=RATE_LABEL,
                y="New Claims",
                hover_data={"Date": True},
                title=f"Unemployment Rate vs. New Claims (r = {corr_new:.3f})",
                labels={
                    RATE_LABEL: "Unemployment Rate (%)",
                    "New Claims": "Monthly New Claims",
                },
                color_discrete_sequence=["#3b82f6"],
            )
            fig_new.update_layout(height=400)
            st.plotly_chart(fig_new, use_container_width=True)

        with sc2:
            fig_cont = px.scatter(
                merged,
                x=RATE_LABEL,
                y="Continued Claims",
                hover_data={"Date": True},
                title=f"Unemployment Rate vs. Continued Claims (r = {corr_cont:.3f})",
                labels={
                    RATE_LABEL: "Unemployment Rate (%)",
                    "Continued Claims": "Monthly Continued Claims",
                },
                color_discrete_sequence=["#9ABDDC"],
            )
            fig_cont.update_layout(height=400)
            st.plotly_chart(fig_cont, use_container_width=True)

        # dual-axis time series overlay
        st.subheader("BLS Rate vs. Claims Over Time")
        overlay_tab1, overlay_tab2 = st.tabs(["New Claims", "Continued Claims"])

        with overlay_tab1:
            fig_ov1 = px.line(
                merged,
                x="Date",
                y=[RATE_LABEL, "New Claims"],
                title="BLS Unemployment Rate & Monthly New Claims",
            )
            # secondary y-axis for claims
            fig_ov1 = px.line(merged, x="Date", y=RATE_LABEL, title="BLS Rate vs. New Claims")
            fig_ov1.add_scatter(
                x=merged["Date"],
                y=merged["New Claims"],
                name="New Claims",
                yaxis="y2",
                line={"color": "#3b82f6"},
            )
            fig_ov1.update_layout(
                yaxis={"title": "Unemployment Rate (%)"},
                yaxis2={"title": "Monthly New Claims", "overlaying": "y", "side": "right"},
                height=450,
                legend={"orientation": "h", "y": -0.15},
            )
            st.plotly_chart(fig_ov1, use_container_width=True)

        with overlay_tab2:
            fig_ov2 = px.line(merged, x="Date", y=RATE_LABEL, title="BLS Rate vs. Continued Claims")
            fig_ov2.add_scatter(
                x=merged["Date"],
                y=merged["Continued Claims"],
                name="Continued Claims",
                yaxis="y2",
                line={"color": "#9ABDDC"},
            )
            fig_ov2.update_layout(
                yaxis={"title": "Unemployment Rate (%)"},
                yaxis2={
                    "title": "Monthly Continued Claims",
                    "overlaying": "y",
                    "side": "right",
                },
                height=450,
                legend={"orientation": "h", "y": -0.15},
            )
            st.plotly_chart(fig_ov2, use_container_width=True)

    st.divider()
