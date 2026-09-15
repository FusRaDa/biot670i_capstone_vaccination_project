import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import pearsonr, spearmanr

st.set_page_config(page_title="Time-Lagged Association: Vaccine Coverage & Disease Cases", page_icon="⏱️")

st.markdown("Time-Lagged Association: Vaccine Coverage & Disease Cases")
st.sidebar.header("Time-Lagged Association")

st.write(
    """
    ### Time-Lagged Association - Pooled Analysis

    This analysis tests whether vaccination coverage in a previous year is associated with disease incidence in a later year.

    Vaccination coverage is lagged by one year, so each year's disease cases are compared with the vaccination coverage from the preceding year. 
    This helps account for the fact that changes in population-level vaccination coverage may not have an immediate effect on disease incidence.

    A negative association would indicate that higher vaccination coverage in the previous year is associated with fewer reported cases in the following year.
    """
)

cases_df = pd.read_csv('app/data/tycho_cases.csv')
coverage_df = pd.read_csv('app/data/nis_vacc_coverage.csv')

yearly_coverage_cases_df = pd.merge(cases_df, coverage_df, on=['year', 'state'])

# Sort by state and year
lagged_df = yearly_coverage_cases_df.sort_values(
    ["state", "year"]
).copy()

diseases = ["measles", "mumps", "pertussis"]

# Previous year within each state
lagged_df["previous_year"] = (
    lagged_df.groupby("state")["year"].shift(1)
)

# Create 1-year lagged coverage for each disease
for disease in diseases:

    coverage_col = f"{disease}_coverage_pct"
    lag_col = f"{disease}_coverage_lag1"

    # Get coverage from previous observation
    lagged_df[lag_col] = (
        lagged_df.groupby("state")[coverage_col].shift(1)
    )

    # Only keep it if the observation is exactly one year earlier
    lagged_df[lag_col] = lagged_df[lag_col].where(
        lagged_df["year"] - lagged_df["previous_year"] == 1
    )

# create a dictionary of seperate diseases dfs
lag_dfs = {}

for disease in diseases:

    lag_col = f"{disease}_coverage_lag1"
    cases_col = f"{disease}_cases"

    # Keep only observations with both lagged coverage and cases
    lag_dfs[disease] = lagged_df.dropna(
        subset=[lag_col, cases_col]
    ).copy()


def graph_lagged_coverage_cases(lag_dfs):

    diseases = ["measles", "mumps", "pertussis"]

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

    for col, disease in enumerate(diseases, start=1):

        df = lag_dfs[disease]

        lag_col = f"{disease}_coverage_lag1"
        cases_col = f"{disease}_cases"

        plot_df = df.dropna(
            subset=[lag_col, cases_col]
        ).copy()

        # Pearson correlation
        pearson_r, pearson_p = pearsonr(
            plot_df[lag_col],
            plot_df[cases_col]
        )

        # Spearman correlation
        spearman_rho, spearman_p = spearmanr(
            plot_df[lag_col],
            plot_df[cases_col]
        )

        # Scatter plot
        fig.add_trace(
            go.Scatter(
                x=plot_df[lag_col],
                y=plot_df[cases_col],
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
                    "Previous-year coverage: %{x:.2f}%<br>"
                    "Cases: %{y}<extra></extra>"
                )
            ),
            row=1,
            col=col
        )

        fig.update_xaxes(
            title_text="Previous-Year Coverage (%)",
            row=1,
            col=col
        )

        fig.update_yaxes(
            title_text="Reported Cases",
            row=1,
            col=col
        )

        # Correlations BELOW each graph
        fig.add_annotation(
            x=0.5,
            y=-0.25,
            xref=f"x{col} domain" if col > 1 else "x domain",
            yref="paper",
            text=(
                f"<b>Pearson:</b> r = {pearson_r:.3f}, "
                f"p = {pearson_p:.3g}<br>"
                f"<b>Spearman:</b> ρ = {spearman_rho:.3f}, "
                f"p = {spearman_p:.3g}"
            ),
            showarrow=False,
            align="center",
            font=dict(size=12)
        )

    fig.update_layout(
        title="1-Year Lagged Vaccine Coverage vs. Disease Cases",
        height=650,
        width=1200,
        margin=dict(
            t=80,
            b=140
        ),
        showlegend=False
    )

    return fig


fig = graph_lagged_coverage_cases(lag_dfs)
st.plotly_chart(fig, width="stretch")