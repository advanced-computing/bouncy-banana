import time
from contextlib import contextmanager

import pandas as pd
import plotly.express as px
import streamlit as st
from google.oauth2 import service_account

from src.functions.fred_data import fred_from_bigquery
from src.functions.health_bq import health
from src.utils.styles import apply_global_styles

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# configure browser tab
st.set_page_config(
    page_title="NYC Health & Unemployment",
    page_icon="🗽",
    layout="wide",
)

apply_global_styles()


# cache health data
@st.cache_data
def load_health_bq():
    return health()


@st.cache_data
def load_fred_data():
    return fred_from_bigquery(credentials, "new_insurance_table")


# set up page load time
@contextmanager
def display_load_time():
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        st.caption(f"Page loaded in {elapsed:.2f} seconds")


with display_load_time():
    # load cached data
    health_data = load_health_bq()
    fred_data_cache = load_fred_data()

    # change weekly insurance claims to yearly to match health data
    fred_data_cache["year"] = pd.to_datetime(fred_data_cache["Date"]).dt.year
    fred_yearly = fred_data_cache.groupby("year")["Claims"].sum().reset_index()

    # merge on year
    merged = health_data.merge(fred_yearly, on="year", how="inner")

    # find peak unemployment year
    peak_year = int(fred_yearly.loc[fred_yearly["Claims"].idxmax(), "year"])
    peak_row = merged[merged["year"] == peak_year].iloc[0]

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")

    year_range = st.sidebar.slider(
        "Year Range",
        min_value=2010,
        max_value=2020,
        value=(2010, 2020),
    )

    # apply filter
    filtered_health = health_data[
        (health_data["year"] >= year_range[0]) & (health_data["year"] <= year_range[1])
    ]

    st.title("NYC Health Data")

    # summary metrics
    st.subheader("Key Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Peak Unemployment Year",
            value=f"{peak_year}",
            delta=f"{int(peak_row['Claims']):,} claims",
        )

    with col2:
        st.metric(
            label="Smoking Rate That Year",
            value=f"{peak_row['Smoking Status (current smokers)']}%",
            delta=f"{peak_year}",
        )

    with col3:
        st.metric(
            label="Obesity Rate That Year",
            value=f"{peak_row['Obesity']}%",
            delta=f"{peak_year}",
        )

    st.divider()
    st.subheader("Health Indicators Over Time")

    # define variable groups
    access_to_care = [
        "No Health Insurance",
        "Do not get medical care",
        "No Personal Doctor",
    ]

    lifestyle_risk = [
        "Obesity",
        "Smoking Status (current smokers)",
        "Binge Drinking",
        "Drinks 1 or more sugar-sweetened beverages per day",
    ]

    general_health = [
        "Self-reported Health Status (excellent/very good/good)",
    ]

    all_health_vars = access_to_care + lifestyle_risk + general_health

    # convert to numeric
    filtered_health[all_health_vars] = filtered_health[all_health_vars].apply(
        pd.to_numeric, errors="coerce"
    )

    # aggregate by year
    filtered_health = filtered_health.groupby("year")[all_health_vars].mean().reset_index()

    def make_line_chart(df, variables, title):
        melted = df.melt(
            id_vars="year",
            value_vars=variables,
            var_name="Indicator",
            value_name="Value",
        )

        fig = px.line(
            melted,
            x="year",
            y="Value",
            color="Indicator",
            markers=False,
            title=title,
            labels={"year": "Year", "Value": "Rate (%)"},
        )
        fig.update_layout(
            xaxis=dict(tickmode="linear", dtick=1),
            legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="left", x=0),
            hovermode="x unified",
        )
        return fig

    st.plotly_chart(
        make_line_chart(filtered_health, general_health, "General Health"),
        use_container_width=True,
    )
    st.divider()

    st.plotly_chart(
        make_line_chart(filtered_health, access_to_care, "Access to Care"),
        use_container_width=True,
    )
    st.divider()

    st.plotly_chart(
        make_line_chart(filtered_health, lifestyle_risk, "Lifestyle & Risk Factors"),
        use_container_width=True,
    )
    st.divider()
