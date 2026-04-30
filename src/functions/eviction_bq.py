import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

# Second Dataset
# https://data.cityofnewyork.us/City-Government/Evictions/6z8x-wfk4/about_data


def eviction():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )

    query = """
        SELECT
            executed_date,
            borough,
            longitude,
            latitude,
            eviction_address
        FROM `sipa-adv-c-bouncy-banana.eviction.eviction_table`
    """

    eviction_data = client.query(query).to_dataframe()

    eviction_data["executed_date"] = pd.to_datetime(eviction_data["executed_date"])
    eviction_data["longitude"] = pd.to_numeric(eviction_data["longitude"], errors="coerce")
    eviction_data["latitude"] = pd.to_numeric(eviction_data["latitude"], errors="coerce")

    return eviction_data


def borough_count(eviction_data_clean):
    eviction_data_group = eviction_data_clean.groupby("borough").size().reset_index(name="Count")

    return eviction_data_group
