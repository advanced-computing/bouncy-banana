import pandas as pd
import requests
from google.cloud import bigquery


def fetch_fred(series_id, api_key, column_name):
    url = "https://api.stlouisfed.org/fred/series/observations"

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "frequency": "w",
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    df = pd.DataFrame(data["observations"])
    df["Date"] = pd.to_datetime(df["date"])
    df[column_name] = pd.to_numeric(df["value"], errors="coerce")
    df = df.drop(columns=["date", "value", "realtime_start", "realtime_end"])
    df = df.dropna()

    return df


def fred_from_bigquery(credentials, table_name):
    client = bigquery.Client(
        credentials=credentials,
        project="sipa-adv-c-bouncy-banana",
    )

    query = """
        SELECT *
        FROM `sipa-adv-c-bouncy-banana.new_insurance.continued_insurance_table`
    """

    df = client.query(query).to_dataframe()
    df["Date"] = pd.to_datetime(df["Date"])
    return df
