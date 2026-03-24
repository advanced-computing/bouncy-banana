import duckdb
import pandas_gbq
import pydata_google_auth

from eviction import eviction

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
df = eviction()

# Inspect locally with DuckDB before sending to BigQuery
con = duckdb.connect()
con.execute("CREATE TABLE eviction_table AS SELECT * FROM df")
print(con.sql("SELECT * FROM eviction_table").fetchdf())
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
