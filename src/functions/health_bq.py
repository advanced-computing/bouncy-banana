import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

column_rename = {
    "prevelance": "Prevelance",
    "q_1": "No Health Insurance",
    "q_2": "Do not get medical care",
    "q_3": "No Personal Doctor",
    "q_4": "Drinks 1 or more sugar-sweetened beverages per day",
    "q_5": "Smoking Status (current smokers)",
    "q_6": "Obesity",
    "q_7": "Binge Drinking",
    "q_8": "Colon cancer screening, adults age 50+ (colonoscopy)",
    "q_9": "Self-reported Health Status (excellent/very good/good)",
    "q_10": "Flu shot in last 12 months, adults ages 65+ (not age-adjusted)",
}


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
    health_data = health_data.rename(columns=column_rename)

    return health_data
