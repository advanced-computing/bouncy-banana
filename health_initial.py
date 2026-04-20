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

    health_data = health_data.rename(
        columns={
            "prevelance": "Prevelance",
            "q_1": "No Health Insurance",
            "q_2": "Do not get medical care",
            "q_3": "No Personal Doctor",
            "q_4": "Drinks 1 or more sugar-sweetened beverages per day",
            "q_5": "Smoking Status (current smokers)",
            "q_6": "Obesity",
            "q_7": "Binge Drinking",
            "q_8": "Colon cancer screening, adults age 50+ (colonoscopy)",
            "q_9": "Self-reported Health Status (excellent/very good/good)",
            "q_10": "Flu shot in last 12 months, adults ages 65+ (not age-adjusted)",
        }
    )

    health_data["year"] = health_data["year"].astype(int)

    return health_data
