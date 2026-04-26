import pandas as pd
import requests


def fetch_BLS(series_id, api_key, column_name, start_year=1976, end_year=None):
    if end_year is None:
        end_year = pd.Timestamp.now().year

    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    # BLS API caps at 20 years per request, so chunk accordingly
    chunks = []
    year = start_year
    while year <= end_year:
        payload = {
            "seriesid": [series_id],
            "startyear": str(year),
            "endyear": str(min(year + 19, end_year)),
        }
        if api_key:
            payload["registrationkey"] = api_key

        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()

        status = data.get("status", "")
        if status != "REQUEST_SUCCEEDED":
            messages = data.get("message", [])
            raise RuntimeError(f"BLS API error ({status}): {'; '.join(messages)}")

        series_data = data.get("Results", {}).get("series", [])
        if not series_data or not series_data[0].get("data"):
            raise RuntimeError(
                f"BLS returned no data for series '{series_id}' "
                f"({year}–{min(year + 19, end_year)}). "
                "Register a free API key at https://data.bls.gov/registrationEngine/ "
                "and add it as bls_api_key in .streamlit/secrets.toml."
            )
        chunks.extend(series_data[0]["data"])
        year += 20

    df = pd.DataFrame(chunks)
    # keep only monthly periods (M01–M12); skip annual (M13) or semi-annual rows
    df = df[df["period"].str.match(r"^M(0[1-9]|1[0-2])$")]
    df["Date"] = pd.to_datetime(df["year"] + "-" + df["period"].str[1:], format="%Y-%m")
    df[column_name] = pd.to_numeric(df["value"], errors="coerce")
    df = df[["Date", column_name]].dropna().sort_values("Date").reset_index(drop=True)

    for months in [1, 3, 6, 12]:
        df[f"{months}-Month Net Change"] = df[column_name].diff(months).round(1)
        df[f"{months}-Month % Change"] = (df[column_name].pct_change(months) * 100).round(1)

    return df
