import time
from contextlib import contextmanager

import pydeck as pdk
import streamlit as st

from eviction_bq import borough_count, eviction
from utils.styles import apply_global_styles

st.set_page_config(layout="wide")
apply_global_styles()

# configure browser tab
st.set_page_config(
    page_title="NYC Evictions & Unemployment",
    page_icon="🗽",
    layout="wide",
)


@st.cache_data(ttl=3600)
def load_eviction_data():
    df = eviction()
    df = df.dropna(subset=["latitude", "longitude"])
    return df


eviction_data = load_eviction_data()

# --- Sidebar Filters ---
st.sidebar.header("Filters")

boroughs = sorted(eviction_data["borough"].dropna().unique().tolist())
selected_boroughs = st.sidebar.multiselect("Borough", boroughs, default=boroughs)

min_date = eviction_data["executed_date"].min().date()
max_date = eviction_data["executed_date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if st.sidebar.button("Clear Date Range"):
    st.session_state["date_range"] = (min_date, max_date)

# Apply filters
filtered = eviction_data[eviction_data["borough"].isin(selected_boroughs)]
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["executed_date"].dt.date >= start_date)
        & (filtered["executed_date"].dt.date <= end_date)
    ]

# --- Page Title ---
st.title("NYC Eviction Data")

# --- Summary Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Evictions", f"{len(filtered):,}")

if not filtered.empty:
    top_borough = filtered.groupby("borough").size().idxmax()
else:
    top_borough = "N/A"

col2.metric("Most Affected Borough", top_borough)

if not filtered.empty:
    date_label = (
        f"{filtered['executed_date'].min().strftime('%b %Y')} – "
        f"{filtered['executed_date'].max().strftime('%b %Y')}"
    )
else:
    date_label = "N/A"
col3.metric("Date Range", date_label)

# --- Tabs ---
tab_map, tab_trends, tab_borough, tab_data = st.tabs(["Map", "Trends", "By Borough", "Raw Data"])

with tab_map:
    # One HexagonLayer per borough, each with its own color ramp
    BOROUGH_COLOR_RANGES = {
        "BRONX": [[254, 229, 217], [252, 174, 145], [251, 106, 74], [222, 45, 38], [165, 15, 21]],
        "BROOKLYN": [
            [239, 243, 255],
            [189, 215, 231],
            [107, 174, 214],
            [49, 130, 189],
            [8, 81, 156],
        ],
        "MANHATTAN": [
            [242, 240, 247],
            [203, 201, 226],
            [158, 154, 200],
            [117, 107, 177],
            [63, 0, 125],
        ],
        "QUEENS": [[237, 248, 233], [186, 228, 179], [116, 196, 118], [49, 163, 84], [0, 109, 44]],
        "STATEN ISLAND": [
            [255, 255, 212],
            [254, 217, 142],
            [254, 153, 41],
            [217, 95, 14],
            [153, 52, 4],
        ],
    }

    layers = [
        pdk.Layer(
            "HexagonLayer",
            data=filtered[filtered["borough"].str.upper() == borough],
            get_position=["longitude", "latitude"],
            radius=300,
            elevation_scale=4,
            elevation_range=[0, 500],
            extruded=True,
            pickable=True,
            color_range=color_range,
        )
        for borough, color_range in BOROUGH_COLOR_RANGES.items()
        if not filtered[filtered["borough"].str.upper() == borough].empty
    ]

    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=pdk.ViewState(
                latitude=40.7128,
                longitude=-74.0060,
                zoom=10,
                pitch=40,
                min_zoom=9,
                max_zoom=14,
            ),
            map_style="light",
            tooltip={"text": "Evictions: {elevationValue}"},
            views=[
                pdk.View(
                    type="MapView",
                    controller={"maxBounds": [[-74.6, 40.4], [-73.6, 41.0]]},
                )
            ],
        )
    )


with tab_trends:
    st.subheader("Monthly Evictions Over Time")
    monthly = (
        filtered.copy()
        .set_index("executed_date")
        .resample("ME")
        .size()
        .reset_index(name="Evictions")
        .rename(columns={"executed_date": "Month"})
    )
    if monthly.empty:
        st.info("No data for selected filters.")
    else:
        st.line_chart(monthly, x="Month", y="Evictions")

with tab_borough:
    st.subheader("Evictions by Borough")
    borough_df = borough_count(filtered)
    borough_df["% of Total"] = (borough_df["Count"] / borough_df["Count"].sum() * 100).round(
        1
    ).astype(str) + "%"
    st.bar_chart(borough_df, x="borough", y="Count")
    st.dataframe(borough_df, width="stretch", hide_index=True)

with tab_data:
    st.subheader("Eviction Records")
    display_cols = ["executed_date", "borough", "eviction_address"]
    st.dataframe(
        filtered[display_cols].sort_values("executed_date", ascending=False).reset_index(drop=True),
        width="stretch",
    )


@contextmanager
def display_load_time():
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        st.caption(f"Page loaded in {elapsed:.2f} seconds")
