import pandas as pd
import pandas_gbq
import pydata_google_auth
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

from src.functions.eviction_bq import eviction
from src.functions.fred_data import fetch_fred, fred_from_bigquery

PROJECT_ID = "sipa-adv-c-bouncy-banana"
FRED_KEY = "aa9cd57aae80525dc171dbc517b39546"
RATE_LABEL = "Unemployment Rate (%)"
LABOR_LABEL = "Civilian Labor Force"
BOROUGH_ORDER = ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"]

BOROUGH_LABOR_SERIES = {
    "MANHATTAN": "NYNEWY1LFN",
    "BROOKLYN": "NYKING7LFN",
    "QUEENS": "NYQUEE1LFN",
    "BRONX": "NYBRON5LFN",
    "STATEN ISLAND": "NYRICH5LFN",
}

BOROUGH_RATE_SERIES = {
    "MANHATTAN": "NYNEWY1URN",
    "BROOKLYN": "NYKING7URN",
    "QUEENS": "NYQUEE1URN",
    "BRONX": "NYBRON5URN",
    "STATEN ISLAND": "NYRICH5URN",
}

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/drive",
]


def push_borough_labor_to_bq():
    credentials = pydata_google_auth.get_user_credentials(SCOPES, auth_local_webserver=True)
    frames = []
    for borough, series_id in BOROUGH_LABOR_SERIES.items():
        df = fetch_fred(series_id, FRED_KEY, "Labor Force", frequency="m")
        df["Borough"] = borough
        frames.append(df)
    combined = pd.concat(frames)
    combined["Year"] = combined["Date"].dt.year
    pandas_gbq.to_gbq(
        combined,
        "unemployment.borough_labor_table",
        project_id=PROJECT_ID,
        if_exists="append",
        credentials=credentials,
    )


def push_borough_rates_to_bq():
    credentials = pydata_google_auth.get_user_credentials(SCOPES, auth_local_webserver=True)
    frames = []
    for borough, series_id in BOROUGH_RATE_SERIES.items():
        df = fetch_fred(series_id, FRED_KEY, "Rate", frequency="m")
        df["Borough"] = borough
        frames.append(df)
    combined = pd.concat(frames)
    combined["Year"] = combined["Date"].dt.year
    pandas_gbq.to_gbq(
        combined,
        "unemployment.borough_rates_table",
        project_id=PROJECT_ID,
        if_exists="append",
        credentials=credentials,
    )


@st.cache_data
def load_borough_labor():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    query = "SELECT * FROM `sipa-adv-c-bouncy-banana.unemployment.borough_labor_table`"
    df = client.query(query).to_dataframe()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    return df


@st.cache_data
def load_borough_rates():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    query = "SELECT * FROM `sipa-adv-c-bouncy-banana.unemployment.borough_rates_table`"
    df = client.query(query).to_dataframe()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    return df


@st.cache_data(ttl=3600)
def load_ui_claims():
    creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    df = fred_from_bigquery(creds, "new_insurance_table")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby("Month")["Claims"].sum().reset_index()
    return monthly


@st.cache_data(ttl=3600)
def load_eviction_data():
    df = eviction()
    df["Year"] = df["executed_date"].dt.year
    df["Month"] = df["executed_date"].dt.to_period("M").dt.to_timestamp()
    return df


def get_metrics(borough, selected_year, data, ui_annual_total):
    borough_labor_df = data["labor"]
    borough_rates_df = data["rates"]
    eviction_by_borough = data["evictions"]

    labor = borough_labor_df[
        (borough_labor_df["Borough"] == borough) & (borough_labor_df["Year"] == selected_year)
    ]["Labor Force"].mean()
    rate = borough_rates_df[
        (borough_rates_df["Borough"] == borough) & (borough_rates_df["Year"] == selected_year)
    ]["Rate"].mean()
    unemployed = labor * (rate / 100)

    ev_row = eviction_by_borough[eviction_by_borough["borough"] == borough]
    ev_share = ev_row["Eviction Share (%)"].iloc[0] / 100 if not ev_row.empty else 0
    ui_claims = ui_annual_total * ev_share

    evictions = ev_row["Evictions"].iloc[0] if not ev_row.empty else 0

    return {"unemployed": unemployed, "ui_claims": ui_claims, "evictions": evictions}
