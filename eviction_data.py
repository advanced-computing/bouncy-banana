import duckdb
import pandas as pd
import pandas_gbq
import pydata_google_auth
import requests

# https://data.cityofnewyork.us/City-Government/Evictions/6z8x-wfk4/about_data
EVICTION_URL = "https://data.cityofnewyork.us/resource/6z8x-wfk4.json"
COLUMNS = ["executed_date", "borough", "longitude", "latitude", "eviction_address"]


def fetch_eviction_data(limit=50000):
    frames = []
    offset = 0
    while True:
        r = requests.get(
            EVICTION_URL,
            params={
                "$select": ",".join(COLUMNS),
                "$limit": limit,
                "$offset": offset,
                "$order": ":id",
            },
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        frames.append(pd.json_normalize(data))
        if len(data) < limit:
            break
        offset += limit

    df = pd.concat(frames, ignore_index=True).reindex(columns=COLUMNS)
    df["executed_date"] = pd.to_datetime(df["executed_date"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    return df


PROJECT_ID = "sipa-adv-c-bouncy-banana"
DATASET = "eviction"
TABLE = "eviction_table"

# Authenticate
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/drive",
]

credentials = pydata_google_auth.get_user_credentials(
    SCOPES,
    auth_local_webserver=True,
)

# Load and clean data
df = fetch_eviction_data()

# Inspect locally with DuckDB before sending to BigQuery
con = duckdb.connect()
con.execute("CREATE TABLE eviction_table AS SELECT * FROM df")
print(con.sql("SELECT * FROM eviction_table").fetchdf().columns.tolist())
con.close()

# Write to BigQuery
pandas_gbq.to_gbq(
    df, f"{DATASET}.{TABLE}", project_id=PROJECT_ID, if_exists="append", credentials=credentials
)

# Read back from BigQuery to verify
df_new = pandas_gbq.read_gbq(
    f"SELECT * FROM `{DATASET}.{TABLE}`",
    project_id=PROJECT_ID,  # variable, not the string "PROJECT_ID"
    credentials=credentials,
)

print(df_new)
