import sys

import toml

sys.path.insert(
    0,
    "/Users/sophiacain/Desktop/main/Academics/Columbia University/Spring 2026/"
    "advanced computing/bouncy-banana/",
)

from src.functions.dashboard_data import push_borough_labor_to_bq

push_borough_labor_to_bq()
print("Done.")
