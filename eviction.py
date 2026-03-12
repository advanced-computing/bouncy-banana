import pandas as pd
import requests

# Second Dataset

# https://data.cityofnewyork.us/City-Government/Evictions/6z8x-wfk4/about_data


def eviction():
    eviction_data = pd.DataFrame()
    url = "https://data.cityofnewyork.us/resource/6z8x-wfk4.json"
    limit = 1000
    offset = 0
    count = 0
    max_page = 4
    while count != max_page:
        params = {"$limit": limit, "$offset": offset}
        r = requests.get(url, params=params)
        data = r.json()
        clean_pop = pd.json_normalize(data)
        eviction_data = pd.concat([eviction_data, clean_pop])

        # if len(data) < limit:
        #     loop = False
        offset += limit
        count += 1
    eviction_data_clean = eviction_data[["executed_date", "borough","longitude","latitude"]]
    eviction_data_clean["executed_date"] = pd.to_datetime(eviction_data_clean["executed_date"])
    eviction_data_clean["longitude"] = pd.to_numeric(
        eviction_data_clean["longitude"], errors="coerce"
    )
    eviction_data_clean["latitude"] = pd.to_numeric(
        eviction_data_clean["latitude"], errors="coerce"
    )
    return eviction_data_clean


def borough_count(eviction_data_clean):
    eviction_data_group = eviction_data_clean.groupby("borough").size().reset_index(name="Count")

    return eviction_data_group
