import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Measles, Mumps, Pertussis Cases & Coverage", page_icon="💉")

st.markdown("Measles, Mumps, Pertussis Cases & Coverage: 1995 - 2017")
st.sidebar.header("Measles, Mumps, Pertussis Cases & Coverage")
st.write(
    """
    ### Summary

    Vaccination coverage remained relatively stable from 1995–2017, while 
    reported disease cases varied considerably over time.

    - **Measles:** Cases generally declined after the mid-1990s. Case data are
      unavailable from 2003–2015, so the gap should not be interpreted as zero
      cases. The 2016–2017 values come from CDC NNDSS.
    - **Mumps:** Cases remained relatively low through the early 2000s but rose
      sharply in 2016 and 2017 despite consistently high MMR coverage.
    - **Pertussis:** Cases followed a cyclical pattern, including a substantial
      peak around 2012, while vaccination coverage changed comparatively little.

    Overall, the figure does not demonstrate a simple year-to-year relationship
    between national vaccination coverage and reported cases. National totals
    can conceal state-level differences, localized coverage gaps, and outbreaks.
    Therefore, this visualization is descriptive and should not be interpreted
    as evidence of a causal relationship.
    """
)

cases_df = pd.read_csv('app/data/tycho_cases.csv')
coverage_df = pd.read_csv('app/data/nis_vacc_coverage.csv')

yearly_cases_df = cases_df.groupby('year')[['measles_cases', 'mumps_cases', 'pertussis_cases']].sum(min_count=1).reset_index()
yearly_coverage_df = coverage_df.groupby('year')[['measles_coverage_pct', 'mumps_coverage_pct', 'pertussis_coverage_pct']].mean().reset_index()

yearly_coverage_cases_df = pd.merge(yearly_cases_df, yearly_coverage_df, on='year')


diseases = ["measles", "mumps", "pertussis"]

fig = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    specs=[
        [{"secondary_y": True}],
        [{"secondary_y": True}],
        [{"secondary_y": True}]
    ],
    subplot_titles=["Measles", "Mumps", "Pertussis"],
    vertical_spacing=0.10
)

colors = {
    "measles": "#E74C3C",
    "mumps": "#3498DB",
    "pertussis": "#2ECC71"
}

for row, disease in enumerate(diseases, start=1):

    # Annual cases
    fig.add_trace(
        go.Bar(
            x=yearly_coverage_cases_df["year"],
            y=yearly_coverage_cases_df[f"{disease}_cases"],
            name=f"{disease.title()} cases",
            marker_color=colors[disease],
            opacity=0.65,
            hovertemplate=(
                "Year: %{x}<br>"
                "Cases: %{y:,.0f}"
                "<extra></extra>"
            )
        ),
        row=row,
        col=1,
        secondary_y=False
    )

    # Annual vaccination coverage
    fig.add_trace(
        go.Scatter(
            x=yearly_coverage_cases_df["year"],
            y=yearly_coverage_cases_df[f"{disease}_coverage_pct"],
            name=f"{disease.title()} coverage",
            mode="lines+markers",
            line=dict(color="black", width=2),
            marker=dict(size=6),
            hovertemplate=(
                "Year: %{x}<br>"
                "Coverage: %{y:.2f}%"
                "<extra></extra>"
            )
        ),
        row=row,
        col=1,
        secondary_y=True
    )

    fig.update_yaxes(
        title_text="Cases",
        row=row,
        col=1,
        secondary_y=False
    )

    fig.update_yaxes(
        title_text="Coverage (%)",
        row=row,
        col=1,
        secondary_y=True
    )

fig.update_xaxes(
    title_text="Year",
    row=3,
    col=1,
    dtick=1
)

fig.update_layout(
    title="Annual Vaccination Coverage and Reported Cases",
    template="plotly_white",
    height=900,
    hovermode="x unified",
    legend_title="Measure",
    bargap=0.20
)

st.plotly_chart(fig, width="stretch")