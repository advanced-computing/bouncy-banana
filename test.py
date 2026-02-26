# Test Cases

# load libraries
import pandas as pd
import requests

# Test Definition 1


def health_year_filter(data, year, metric):
    filtered = data[data["year"] == str(year)]
    filtered = filtered[filtered["Prevelance"].str.contains("Prevalence")]

    return filtered[str(metric)].iloc[0]


# Test Definition 2


def borough_count(eviction_data_clean):
    eviction_data_group = (
        eviction_data_clean.groupby("borough").size().reset_index(name="Count")
    )

    return eviction_data_group


# Test Definition 3


def date_filter(data, column, year):
    data[str(column)] = pd.to_datetime(data[column])

    return data[data[column].dt.year == year]


# Test Case 1


def test_answer():
    assert health_year_filter(1990) == "Year"
