import duckdb
import pandas_gbq
import pydata_google_auth

from fred_data import fetch_fred

PROJECT_ID = "sipa-adv-c-bouncy-banana"
DATASET = "new_insurance"
TABLE = "continued_insurance_table"

# Authenticate
fred_key = "aa9cd57aae80525dc171dbc517b39546"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/drive",
]

credentials = pydata_google_auth.get_user_credentials(
    SCOPES,
    auth_local_webserver=True,
)

# Load and clean data
df = fetch_fred("NYCCLAIMS", fred_key, "Continued Claims")

# Inspect locally with DuckDB before sending to BigQuery
con = duckdb.connect()
con.execute("CREATE TABLE continued_insurance_table AS SELECT * FROM df")
print(con.sql("SELECT * FROM continued_insurance_table").fetchdf())
con.close()

# Write to BigQuery
pandas_gbq.to_gbq(
    df, f"{DATASET}.{TABLE}", project_id=PROJECT_ID, if_exists="append", credentials=credentials
)

# Read back from BigQuery to verify
df_new = pandas_gbq.read_gbq(
    f"SELECT * FROM `{DATASET}.{TABLE}`",
    project_id=PROJECT_ID,  # variable, not the string "PROJECT_ID"E
    credentials=credentials,
)

print(df_new)
