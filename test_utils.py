import pandas as pd
import pytest

from utils import health_year_filter, borough_count

def test_health_year_filter():
    df = pd.DataFrame({
        "year": ["2020", "2020", "2019"],
        "Prevelance": ["Prevalence", "Prevalence", "Prevalence"],
        "No Health Insurance": [12.6, 6.6, 12.7]
    })

    result = health_year_filter(df, 2020, "No Health Insurance")
    assert result == 12.6

def test_health_year_filter_not_found():
    df = pd.DataFrame({
        "year": ["2020", "2020", "2019"],
        "Prevelance": ["Prevalence", "Prevalence", "Prevalence"],
        "No Health Insurance": [12.6, 6.6, 12.7]
    })

    with pytest.raises(KeyError):
        health_year_filter(df, 2020, "Column does not exist")

def test_borough_count():
    test_df = pd.DataFrame({
        "borough": ["Manhattan",
                    "Brooklyn",
                    "Brooklyn",
                    "Queens",
                    "Manhattan"
                    ]
    })

    result = borough_count(test_df)
    assert result.loc[result["borough"] == "Brooklyn", "Count"].values[0] == 2
    assert result.loc[result["borough"] == "Manhattan", "Count"].values[0] == 2

def test_borough_count_empty():
    df = pd.DataFrame({
        "borough": []
    })

    result = borough_count(df)

    assert result.empty




    
