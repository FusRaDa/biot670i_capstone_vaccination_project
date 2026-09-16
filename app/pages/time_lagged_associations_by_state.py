import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import pearsonr, spearmanr


st.set_page_config(
    page_title="Time-Lagged Association by State",
    page_icon="⏳"
)

st.markdown(
    "Time-Lagged Association: Vaccine Coverage & Disease Incidence"
)

st.sidebar.header("Time-Lagged Association by State")

st.write(
    """
    ### Time-Lagged Association - State-Level Analysis

    This analysis examines whether vaccination coverage in a previous year is
    associated with disease incidence in the following year within individual
    states.

    Vaccination coverage is lagged by one year, so each state's disease
    incidence in a given year is compared with that same state's vaccination
    coverage from the preceding year.

    Disease incidence is expressed as **cases per 100,000 population**, which
    accounts for changes in state population over time.

    A negative association indicates that years with higher vaccination
    coverage were generally followed by years with lower disease incidence
    within the selected state.

    Pearson and Spearman correlations are reported to measure the strength and
    direction of the relationship. The number of available state-year
    observations (n) should also be considered, particularly for states or
    diseases with limited case data.
    """
)


# -------------------------
# Load data
# -------------------------

cases_df = pd.read_csv(
    "app/data/tycho_cases.csv"
)

population_df = pd.read_csv(
    "app/data/population.csv"
)

coverage_df = pd.read_csv(
    "app/data/nis_vacc_coverage.csv"
)


# -------------------------
# Merge datasets
# -------------------------

yearly_coverage_cases_df = pd.merge(
    cases_df,
    coverage_df,
    on=["year", "state"]
)

yearly_coverage_cases_df = pd.merge(
    yearly_coverage_cases_df,
    population_df,
    on=["year", "state"],
    how="left"
)


# -------------------------
# Calculate cases per 100K
# -------------------------

diseases = [
    "measles",
    "mumps",
    "pertussis"
]

for disease in diseases:

    yearly_coverage_cases_df[
        f"{disease}_cases_per_100k"
    ] = (
        yearly_coverage_cases_df[f"{disease}_cases"]
        / yearly_coverage_cases_df["population"]
        * 100_000
    )


# -------------------------
# Sort by state and year
# -------------------------

lagged_df = yearly_coverage_cases_df.sort_values(
    ["state", "year"]
).copy()


# Previous year within each state
lagged_df["previous_year"] = (
    lagged_df
    .groupby("state")["year"]
    .shift(1)
)


# -------------------------
# Create 1-year lagged coverage
# -------------------------

for disease in diseases:

    coverage_col = f"{disease}_coverage_pct"
    lag_col = f"{disease}_coverage_lag1"

    # Get coverage from previous observation
    lagged_df[lag_col] = (
        lagged_df
        .groupby("state")[coverage_col]
        .shift(1)
    )

    # Only keep it if the observation
    # is exactly one year earlier
    lagged_df[lag_col] = lagged_df[lag_col].where(
        lagged_df["year"]
        - lagged_df["previous_year"]
        == 1
    )


# -------------------------
# State selection
# -------------------------

state = st.selectbox(
    "Select State",
    sorted(
        lagged_df["state"]
        .dropna()
        .unique()
    )
)

state_lag_df = lagged_df[
    lagged_df["state"] == state
].copy()


# -------------------------
# Graph
# -------------------------

def graph_state_lagged_coverage(state_df):

    diseases = [
        "measles",
        "mumps",
        "pertussis"
    ]

    colors = {
        "measles": "#E74C3C",
        "mumps": "#3498DB",
        "pertussis": "#2ECC71"
    }

    state = state_df["state"].iloc[0]

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[
            "Measles",
            "Mumps",
            "Pertussis"
        ]
    )

    for col, disease in enumerate(
        diseases,
        start=1
    ):

        lag_col = f"{disease}_coverage_lag1"

        incidence_col = (
            f"{disease}_cases_per_100k"
        )

        # Drop missing values separately
        # for each disease
        plot_df = state_df.dropna(
            subset=[
                lag_col,
                incidence_col
            ]
        ).copy()


        # -------------------------
        # Correlations
        # -------------------------

        pearson_r, pearson_p = pearsonr(
            plot_df[lag_col],
            plot_df[incidence_col]
        )

        spearman_rho, spearman_p = spearmanr(
            plot_df[lag_col],
            plot_df[incidence_col]
        )


        # -------------------------
        # Scatter plot
        # -------------------------

        fig.add_trace(
            go.Scatter(
                x=plot_df[lag_col],
                y=plot_df[incidence_col],
                mode="markers",
                marker=dict(
                    color=colors[disease],
                    opacity=0.6
                ),
                text=plot_df["year"].astype(str),
                hovertemplate=(
                    "<b>Year: %{text}</b><br>"
                    "Previous-year coverage: "
                    "%{x:.2f}%<br>"
                    "Cases per 100K: "
                    "%{y:.2f}"
                    "<extra></extra>"
                ),
                showlegend=False
            ),
            row=1,
            col=col
        )


        # -------------------------
        # Axes
        # -------------------------

        fig.update_xaxes(
            title_text=(
                "Previous-Year Coverage (%)"
            ),
            row=1,
            col=col
        )

        fig.update_yaxes(
            title_text="Cases per 100K",
            row=1,
            col=col
        )


        # -------------------------
        # Statistics below graph
        # -------------------------

        fig.add_annotation(
            x=0.5,
            y=-0.25,
            xref=(
                f"x{col} domain"
                if col > 1
                else "x domain"
            ),
            yref="paper",
            text=(
                f"<b>n = {len(plot_df)}</b><br>"
                f"Pearson: "
                f"r = {pearson_r:.3f}, "
                f"p = {pearson_p:.3g}<br>"
                f"Spearman: "
                f"ρ = {spearman_rho:.3f}, "
                f"p = {spearman_p:.3g}"
            ),
            showarrow=False,
            align="center",
            font=dict(size=11)
        )


    fig.update_layout(
        title=(
            f"{state}: 1-Year Lagged Vaccine Coverage "
            "vs. Disease Incidence"
        ),
        height=650,
        width=1200,
        margin=dict(
            t=80,
            b=140
        )
    )

    return fig


fig = graph_state_lagged_coverage(
    state_lag_df
)

st.plotly_chart(
    fig,
    width="stretch"
)