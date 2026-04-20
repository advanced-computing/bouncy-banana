import pandas as pd
import requests


def fetch_health_data():
    health_data = pd.DataFrame()
    url = "https://data.cityofnewyork.us/resource/csut-3wpr.json"
    limit = 1000
    offset = 0
    loop = True

    while loop:
        params = {"$limit": limit, "$offset": offset}
        r = requests.get(url, params=params)
        data = r.json()
        clean_pop = pd.json_normalize(data)
        health_data = pd.concat([health_data, clean_pop])

        if len(data) < limit:
            loop = False

        offset += limit

    health_data["year"] = health_data["year"].astype(int)

    return health_data
