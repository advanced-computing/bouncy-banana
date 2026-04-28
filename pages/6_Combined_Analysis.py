import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import streamlit as st
from google.oauth2 import service_account

from eviction_bq import eviction
from fred_data import fetch_fred, fred_from_bigquery
from utils.styles import apply_global_styles

st.set_page_config(
    page_title="Unemployment & Evictions Combined",
    page_icon="🗽",
    layout="wide",
)

apply_global_styles()

FRED_KEY = "aa9cd57aae80525dc171dbc517b39546"
RATE_LABEL = "Unemployment Rate (%)"
LABOR_LABEL = "Civilian Labor Force"
BOROUGH_ORDER = ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"]

BOROUGH_LABOR_SERIES = {
    "MANHATTAN": "NYNEWY1LFN",
    "BROOKLYN": "NYKING7LFN",
    "QUEENS": "NYQUEE1LFN",
    "BRONX": "NYBRON5LFN",
    "STATEN ISLAND": "NYRICH5LFN",
}

BOROUGH_RATE_SERIES = {
    "MANHATTAN": "NYNEWY1URN",
    "BROOKLYN": "NYKING7URN",
    "QUEENS": "NYQUEE1URN",
    "BRONX": "NYBRON5URN",
    "STATEN ISLAND": "NYRICH5URN",
}


def info_box(text: str):
    st.markdown(
        f"""
        <div style="
            background-color:#E5F3FD;
            padding:20px;
            border-radius:8px;
            border-left:6px solid #9ABDDC;
            font-size:17px;
        ">{text}</div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_borough_labor():
    """Raw monthly labor force by borough. Aggregate downstream as needed."""
    frames = []
    for borough, series_id in BOROUGH_LABOR_SERIES.items():
        df = fetch_fred(series_id, FRED_KEY, "Labor Force", frequency="m")
        df["Borough"] = borough
        frames.append(df)
    combined = pd.concat(frames)
    combined["Year"] = combined["Date"].dt.year
    return combined


@st.cache_data
def load_borough_rates():
    """Raw monthly unemployment rate by borough. Aggregate downstream as needed."""
    frames = []
    for borough, series_id in BOROUGH_RATE_SERIES.items():
        df = fetch_fred(series_id, FRED_KEY, "Rate", frequency="m")
        df["Borough"] = borough
        frames.append(df)
    combined = pd.concat(frames)
    combined["Year"] = combined["Date"].dt.year
    return combined



@st.cache_data(ttl=3600)
def load_ui_claims():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    df = fred_from_bigquery(creds, "new_insurance_table")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby("Month")["Claims"].sum().reset_index()
    return monthly


@st.cache_data(ttl=3600)
def load_eviction_data():
    df = eviction()
    df["Year"] = df["executed_date"].dt.year
    df["Month"] = df["executed_date"].dt.to_period("M").dt.to_timestamp()
    return df


st.title("NYC Unemployment & Evictions: Combined Analysis")
st.caption(
    "Sources: FRED (borough-level civilian labor force series, NYUR unemployment rate), "
    "NYC Open Data (Evictions)"
)

borough_labor_df = load_borough_labor()
borough_rates_df = load_borough_rates()
eviction_df = load_eviction_data()

# Aggregate for year filter and top-level metrics
labor_by_year = (
    borough_labor_df.groupby("Year")["Labor Force"]
    .sum()
    .reset_index()
    .rename(columns={"Labor Force": LABOR_LABEL})
)
rate_by_year = (
    borough_rates_df.groupby("Year")["Rate"]
    .mean()
    .reset_index()
    .rename(columns={"Rate": RATE_LABEL})
)

# ── Year filter ───────────────────────────────────────────────────────────────
labor_years = set(labor_by_year["Year"].unique())
rate_years = set(rate_by_year["Year"].unique())
eviction_years = set(eviction_df["Year"].dropna().astype(int).unique())
common_years = sorted(labor_years & rate_years & eviction_years, reverse=True)

if not common_years:
    st.error("No overlapping years found across all three datasets.")
    st.stop()

selected_year = st.selectbox("Select Year", common_years, index=0)

# ── Compute annual figures for selected year ──────────────────────────────────
labor_year_avg = labor_by_year[labor_by_year["Year"] == selected_year][LABOR_LABEL].mean()
rate_year_avg = rate_by_year[rate_by_year["Year"] == selected_year][RATE_LABEL].mean()

total_labor_force = labor_year_avg
total_unemployed = int(total_labor_force * (rate_year_avg / 100))

st.subheader(f"Key Metrics — {selected_year}")
c1, c2, c3 = st.columns(3)
c1.metric("NYC Metro Civilian Labor Force", f"{total_labor_force:,.0f}")
c2.metric("Avg Unemployment Rate (NY State)", f"{rate_year_avg:.1f}%")
c3.metric("Estimated Total Unemployed", f"{total_unemployed:,}")

info_box(
    f"The estimated <b>{total_unemployed:,}</b> unemployed people in {selected_year} is "
    "calculated by multiplying the total NYC civilian labor force (sum of five borough-level "
    "FRED series) by the average unemployment rate across the five boroughs "
    "(FRED: NYNEWY1URN, NYKING7URN, NYQUEE1URN, NYBRON5URN, NYRICH5URN)."
)

st.divider()

# ── Borough distribution via eviction share ───────────────────────────────────
st.header("Estimated Unemployed by Borough")
st.caption(
    "Each borough's share of total evictions for the selected year is used as a "
    "proxy to distribute the estimated unemployed population."
)

eviction_year_df = eviction_df[eviction_df["Year"] == selected_year]
eviction_by_borough = (
    eviction_year_df.groupby("borough").size().reset_index(name="Evictions")
)
eviction_by_borough["borough"] = eviction_by_borough["borough"].str.upper()
eviction_by_borough = eviction_by_borough[
    eviction_by_borough["borough"].isin(BOROUGH_ORDER)
].copy()

if eviction_by_borough.empty:
    st.warning(f"No eviction data available for {selected_year}.")
else:
    total_evictions = eviction_by_borough["Evictions"].sum()
    eviction_by_borough["Eviction Share (%)"] = (
        eviction_by_borough["Evictions"] / total_evictions * 100
    ).round(1)
    eviction_by_borough["Est. Unemployed"] = (
        eviction_by_borough["Eviction Share (%)"] / 100 * total_unemployed
    ).astype(int)
    eviction_by_borough = eviction_by_borough.sort_values(
        "Evictions", ascending=False
    ).reset_index(drop=True)

    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        fig_pie = px.pie(
            eviction_by_borough,
            names="borough",
            values="Est. Unemployed",
            title=f"Estimated Unemployed by Borough ({selected_year})",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.35,
        )
        fig_pie.update_traces(texttemplate="%{label}<br>%{percent}", textposition="outside")
        fig_pie.update_layout(height=420, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_table:
        display_df = eviction_by_borough[
            ["borough", "Evictions", "Eviction Share (%)", "Est. Unemployed"]
        ].rename(columns={"borough": "Borough"})
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    info_box(
        "Each borough's eviction share acts as a proxy for economic distress concentration."
        "This is a distributional estimate — not a direct measurement."
    )

st.divider()

# ── Bronx vs. Manhattan: three-metric comparison ─────────────────────────────
st.header("Bronx vs. Manhattan: Unemployment, UI Claims & Evictions")
st.caption(
    f"All three metrics for the selected year ({selected_year}). "
    "Each panel uses its own scale so no metric is dwarfed by another."
)

ui_claims_df = load_ui_claims()

if not eviction_by_borough.empty:
    ui_annual_total = ui_claims_df[
        ui_claims_df["Month"].dt.year == selected_year
    ]["Claims"].sum()

    def get_metrics(borough: str) -> dict:
        # Est. unemployed: direct borough labor force × borough rate
        labor = borough_labor_df[
            (borough_labor_df["Borough"] == borough) & (borough_labor_df["Year"] == selected_year)
        ]["Labor Force"].mean()
        rate = borough_rates_df[
            (borough_rates_df["Borough"] == borough) & (borough_rates_df["Year"] == selected_year)
        ]["Rate"].mean()
        unemployed = labor * (rate / 100)

        # UI claims apportioned by eviction share
        ev_row = eviction_by_borough[eviction_by_borough["borough"] == borough]
        ev_share = ev_row["Eviction Share (%)"].values[0] / 100 if not ev_row.empty else 0
        ui_claims = ui_annual_total * ev_share

        # Evictions from raw data
        evictions = ev_row["Evictions"].values[0] if not ev_row.empty else 0

        return {"unemployed": unemployed, "ui_claims": ui_claims, "evictions": evictions}

    bronx = get_metrics("BRONX")
    manhattan = get_metrics("MANHATTAN")

    boroughs = ["Bronx", "Manhattan"]
    colors = ["#ef4444", "#3b82f6"]

    ch1, ch2 = st.columns(2)

    with ch1:
        fig_unemp = go.Figure(go.Bar(
            x=boroughs,
            y=[bronx["unemployed"], manhattan["unemployed"]],
            marker_color=colors,
            text=[f"{bronx['unemployed']:,.0f}", f"{manhattan['unemployed']:,.0f}"],
            textposition="outside",
        ))
        fig_unemp.update_layout(
            title=f"Est. Unemployed — {selected_year}",
            height=420,
            showlegend=False,
            margin={"t": 60, "b": 40},
            yaxis={
                "title": "People",
                "range": [0, max(bronx["unemployed"], manhattan["unemployed"]) * 1.2],
            },
        )
        st.plotly_chart(fig_unemp, use_container_width=True)

    with ch2:
        fig_evict = go.Figure(go.Bar(
            x=boroughs,
            y=[bronx["evictions"], manhattan["evictions"]],
            marker_color=colors,
            text=[f"{bronx['evictions']:,}", f"{manhattan['evictions']:,}"],
            textposition="outside",
        ))
        fig_evict.update_layout(
            title=f"Evictions — {selected_year}",
            height=420,
            showlegend=False,
            margin={"t": 60, "b": 40},
            yaxis={
                "title": "Evictions",
                "range": [0, max(bronx["evictions"], manhattan["evictions"]) * 1.2],
            },
        )
        st.plotly_chart(fig_evict, use_container_width=True)

    info_box(
        "The compelling story: the Bronx and Manhattan have <b>similar unemployment counts</b> "
        "but the Bronx sees roughly <b>3× more evictions</b>. This gap — similar job loss, "
        "dramatically different housing outcomes — points to the buffer that income, savings, "
        "and benefits access provide in Manhattan but not the Bronx."
    )

st.divider()

# ── Unemployment by borough over time ─────────────────────────────────────────
st.header("Estimated Unemployed by Borough Over Time")
st.caption(
    "Annual estimated unemployed per borough, derived from the yearly eviction share "
    "applied to the total unemployed figure for each year."
)

trend_rows = []
for yr in common_years:
    lf = labor_by_year[labor_by_year["Year"] == yr][LABOR_LABEL].mean()
    rt = rate_by_year[rate_by_year["Year"] == yr][RATE_LABEL].mean()
    total_unemp_yr = lf * (rt / 100)

    ev_yr = eviction_df[eviction_df["Year"] == yr]
    ev_by_b = ev_yr.groupby("borough").size().reset_index(name="Evictions")
    ev_by_b["borough"] = ev_by_b["borough"].str.upper()
    ev_by_b = ev_by_b[ev_by_b["borough"].isin(BOROUGH_ORDER)]

    if ev_by_b.empty:
        continue

    total_ev_yr = ev_by_b["Evictions"].sum()
    for _, row in ev_by_b.iterrows():
        trend_rows.append(
            {
                "Year": yr,
                "Borough": row["borough"],
                "Est. Unemployed": int(row["Evictions"] / total_ev_yr * total_unemp_yr),
            }
        )

if trend_rows:
    trend_df = pd.DataFrame(trend_rows).sort_values("Year")
    fig_trend = px.line(
        trend_df,
        x="Year",
        y="Est. Unemployed",
        color="Borough",
        markers=True,
        title="Estimated Unemployed by Borough Over Time",
        labels={"Est. Unemployed": "Estimated Unemployed", "Year": "Year"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_trend.update_layout(height=480, legend={"orientation": "h", "y": -0.15})
    st.plotly_chart(fig_trend, use_container_width=True)
