import requests
import pandas as pd


def fetch_fred(series_id, api_key, column_name):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "frequency": "w",
    }
    r = requests.get(url, params = params)
    data = r.json()
    df = pd.DataFrame(data["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop(columns = ["realtime_start", "realtime_end"])

    df = df.rename(columns = {"value": column_name})
    df = df.rename(columns = {"date": "Date"})
    df[column_name] = pd.to_numeric(df[column_name])
    return df