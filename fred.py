import pandas as pd
import requests


def fetch_fred(series_id, api_key, column_name):
    url = "https://api.stlouisfed.org/fred/series/observations"

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "frequency": "w",
    }

    r = requests.get(url, params=params)
    data = r.json()

    df = pd.DataFrame(data["observations"])
    df["Date"] = pd.to_datetime(df["date"])
    df[column_name] = pd.to_numeric(df["value"], errors="coerce")
    df = df.drop(columns=["date", "value", "realtime_start", "realtime_end"])
    df = df.dropna()

    return df
