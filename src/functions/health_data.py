import duckdb
import pandas_gbq
import pydata_google_auth

from src.functions.health_initial import fetch_health_data

PROJECT_ID = "sipa-adv-c-bouncy-banana"
DATASET = "health"
TABLE = "health_table"

# Authenticate
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/drive",
]

credentials = pydata_google_auth.get_user_credentials(
    SCOPES,
    auth_local_webserver=True,
)

# Fetch from API
df = fetch_health_data()

# Inspect locally with DuckDB before sending to BigQuery
con = duckdb.connect()
con.execute("CREATE TABLE health_table AS SELECT * FROM df")
print(con.sql("SELECT * FROM health_table").fetchdf().columns.tolist())
con.close()

# Incremental load: only insert records newer than what's already in BigQuery
try:
    existing = pandas_gbq.read_gbq(
        f"SELECT MAX(year) as max_year FROM `{PROJECT_ID}.{DATASET}.{TABLE}`",
        project_id=PROJECT_ID,
        credentials=credentials,
    )
    max_year = existing["max_year"].iloc[0]
    df = df[df["year"].astype(str) > str(max_year)]
except Exception:
    pass  # table doesn't exist yet, insert all records

if not df.empty:
    pandas_gbq.to_gbq(
        df, f"{DATASET}.{TABLE}", project_id=PROJECT_ID, if_exists="append", credentials=credentials
    )

print("Upload complete.")
