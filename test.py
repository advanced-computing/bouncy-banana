from fred_data import fred_from_bigquery
from health_bq import health

df_unemployment = fred_from_bigquery()
df_health = health()

print("=== UNEMPLOYMENT ===")
print(df_unemployment.head())
print(df_unemployment.dtypes)

print("=== HEALTH ===")
print(df_health.head())
print(df_health.dtypes)
