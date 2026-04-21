from health_bq import health

health_data = health()
print(health_data["year"].min(), health_data["year"].max())
