import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)


def health():
    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )

    query = """
        SELECT *
        FROM `sipa-adv-c-bouncy-banana.health.health_table`
    """

    health_data = client.query(query).to_dataframe()

    health_data["year"] = health_data["year"].astype(int)

    return health_data
