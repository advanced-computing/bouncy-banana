import pandas as pd
import pytest

from .utils import borough_count, health_year_filter


def test_health_year_filter():
    df = pd.DataFrame(
        {
            "year": ["2020", "2020", "2019"],
            "Prevelance": ["Prevalence", "Prevalence", "Prevalence"],
            "No Health Insurance": [12.6, 6.6, 12.7],
        }
    )

    result = health_year_filter(df, 2020, "No Health Insurance")
    health_expected_value = 12.6
    assert result == health_expected_value


def test_health_year_filter_not_found():
    df = pd.DataFrame(
        {
            "year": ["2020", "2020", "2019"],
            "Prevelance": ["Prevalence", "Prevalence", "Prevalence"],
            "No Health Insurance": [12.6, 6.6, 12.7],
        }
    )

    with pytest.raises(KeyError):
        health_year_filter(df, 2020, "Column does not exist")


def test_borough_count():
    test_df = pd.DataFrame(
        {"borough": ["Manhattan", "Brooklyn", "Brooklyn", "Queens", "Manhattan"]}
    )

    result = borough_count(test_df)
    borough_expected_value = 2
    brooklyn_count = result.loc[result["borough"] == "Brooklyn", "Count"].to_numpy()[0]
    manhattan_count = result.loc[result["borough"] == "Manhattan", "Count"].to_numpy()[0]
    assert brooklyn_count == borough_expected_value
    assert manhattan_count == borough_expected_value


def test_borough_count_empty():
    df = pd.DataFrame({"borough": []})

    result = borough_count(df)

    assert result.empty
