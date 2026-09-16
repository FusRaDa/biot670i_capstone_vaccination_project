import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import pearsonr, spearmanr

st.set_page_config(
    page_title="Time-Lagged Association: Vaccine Coverage & Disease Incidence",
    page_icon="⏱️"
)

st.markdown(
    "Time-Lagged Association: Vaccine Coverage & Disease Incidence"
)

st.sidebar.header("Time-Lagged Association")

st.write(
    """
    ### Time-Lagged Association - Pooled Analysis

    This analysis tests whether vaccination coverage in a previous year is
    associated with disease incidence in a later year.

    Vaccination coverage is lagged by one year, so each year's disease incidence
    is compared with vaccination coverage from the preceding year. Disease
    incidence is expressed as **cases per 100,000 population**, which accounts
    for differences in population size between states.

    A negative association would indicate that higher vaccination coverage in
    the previous year is associated with lower disease incidence in the
    following year.

    Pearson correlation measures the linear association between previous-year
    vaccination coverage and disease incidence, while Spearman correlation
    measures whether the variables have a monotonic relationship.
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
    lagged_df.groupby("state")["year"].shift(1)
)


# -------------------------
# Create 1-year lagged coverage
# -------------------------

for disease in diseases:

    coverage_col = f"{disease}_coverage_pct"
    lag_col = f"{disease}_coverage_lag1"

    # Get coverage from previous observation
    lagged_df[lag_col] = (
        lagged_df.groupby("state")[coverage_col].shift(1)
    )

    # Only keep coverage if observation
    # is exactly one year earlier
    lagged_df[lag_col] = lagged_df[lag_col].where(
        lagged_df["year"]
        - lagged_df["previous_year"]
        == 1
    )


# -------------------------
# Separate disease dataframes
# -------------------------

lag_dfs = {}

for disease in diseases:

    lag_col = f"{disease}_coverage_lag1"
    incidence_col = f"{disease}_cases_per_100k"

    # Keep only observations with both
    # lagged coverage and incidence
    lag_dfs[disease] = lagged_df.dropna(
        subset=[
            lag_col,
            incidence_col
        ]
    ).copy()


# -------------------------
# Graph
# -------------------------

def graph_lagged_coverage_cases(lag_dfs):

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

        df = lag_dfs[disease]

        lag_col = f"{disease}_coverage_lag1"
        incidence_col = (
            f"{disease}_cases_per_100k"
        )

        plot_df = df.dropna(
            subset=[
                lag_col,
                incidence_col
            ]
        ).copy()


        # -------------------------
        # Pearson correlation
        # -------------------------

        pearson_r, pearson_p = pearsonr(
            plot_df[lag_col],
            plot_df[incidence_col]
        )


        # -------------------------
        # Spearman correlation
        # -------------------------

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
                name=disease.capitalize(),
                marker=dict(
                    color=colors[disease],
                    opacity=0.5
                ),
                text=(
                    plot_df["state"]
                    + " - "
                    + plot_df["year"].astype(str)
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Previous-year coverage: "
                    "%{x:.2f}%<br>"
                    "Cases per 100K: "
                    "%{y:.2f}"
                    "<extra></extra>"
                )
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
        # Correlations
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
                f"<b>Pearson:</b> "
                f"r = {pearson_r:.3f}, "
                f"p = {pearson_p:.3g}<br>"
                f"<b>Spearman:</b> "
                f"ρ = {spearman_rho:.3f}, "
                f"p = {spearman_p:.3g}"
            ),
            showarrow=False,
            align="center",
            font=dict(size=12)
        )


    fig.update_layout(
        title=(
            "1-Year Lagged Vaccine Coverage "
            "vs. Disease Incidence"
        ),
        height=650,
        width=1200,
        margin=dict(
            t=80,
            b=140
        ),
        showlegend=False
    )

    return fig


fig = graph_lagged_coverage_cases(
    lag_dfs
)

st.plotly_chart(
    fig,
    width="stretch"
)