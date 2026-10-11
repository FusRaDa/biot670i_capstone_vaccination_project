
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# BIOT 670I CAPSTONE PROJECT - GROUP 1
# State Case Studies: California and Florida
# ============================================================


# ------------------------------------------------------------
# 1. CONFIGURATION
# ------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

COLORS = {
    "early": "#70BDF2",
    "recent": "#087CE5",
    "positive": "#49BFA0",
    "negative": "#E18A8A",
}

# Plotly chart configuration
# Legends are intentionally hidden to prevent the
# unwanted "undefined" legend heading.

def format_historical_chart(fig, y_title):

    fig.update_layout(
        template="plotly_dark",
        title_text="",
        showlegend=False,
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        margin=dict(
            l=60,
            r=30,
            t=25,
            b=110
        ),

        xaxis=dict(
            title_text="Year",
            type="linear",
            tickmode="linear",
            tick0=1995,
            dtick=1,
            tickangle=60,
            tickfont=dict(size=10),
            range=[1994.5, 2017.5],
            showgrid=False,
            automargin=True
        ),

        yaxis=dict(
            title_text=y_title,
            showgrid=True,
            gridcolor="rgba(150,150,150,0.20)",
            automargin=True
        ),

        hovermode="closest"
    )

    return fig


def display_period_key():
    """Display observation-period labels outside Plotly."""

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            ":blue[**1995–2002:** Earlier observations]"
        )

    with col2:
        st.markdown(
            "**2016–2017:** Recent observations"
        )


@st.cache_data
def load_california_data():

    analysis = pd.read_csv(
        DATA_DIR / "california_measles_analysis.csv"
    )

    lag_results = pd.read_csv(
        DATA_DIR / "california_measles_lag_results.csv"
    )

    return analysis, lag_results


# ------------------------------------------------------------
# 2. DASHBOARD HEADER
# ------------------------------------------------------------

st.title("State Case Studies")

st.caption("BIOT 670I Capstone Project | Group 1")

st.markdown(
    """
    Explore population-level associations between vaccination
    coverage and vaccine-preventable disease incidence.

    This dashboard examines historical trends, time-lagged
    associations, and methodological limitations in
    California and Florida.
    """
)

st.divider()


# ------------------------------------------------------------
# 3. STATE SELECTION
# ------------------------------------------------------------

state = st.selectbox(
    "Select a State",
    ["California", "Florida"]
)


# ============================================================
# 4. CALIFORNIA CASE STUDY
# ============================================================

if state == "California":

    st.header("California: Measles Analysis")

    st.info(
        "Available observations: 1995–2002 and 2016–2017. "
        "Data are unavailable for 2003–2015."
    )

    # --------------------------------------------------------
    # LOAD AND VALIDATE DATA
    # --------------------------------------------------------

    try:
        analysis_df, lag_df = load_california_data()

    except (FileNotFoundError, pd.errors.EmptyDataError) as error:
        st.error(
            "California data could not be loaded. "
            "Verify both CSV files exist in app/data."
        )
        st.exception(error)
        st.stop()

    required_analysis = [
        "year",
        "measles_coverage_pct",
        "measles_cases_per_100k"
    ]

    required_lag = [
        "lag_years",
        "pearson_r",
        "p_value",
        "n"
    ]

    if not set(required_analysis).issubset(analysis_df.columns):
        st.error("The California analysis CSV is missing columns.")
        st.stop()

    if not set(required_lag).issubset(lag_df.columns):
        st.error("The California lag CSV is missing columns.")
        st.stop()

    analysis_df = analysis_df.copy()
    lag_df = lag_df.copy()

    for column in required_analysis:
        analysis_df[column] = pd.to_numeric(
            analysis_df[column],
            errors="coerce"
        )

    for column in required_lag:
        lag_df[column] = pd.to_numeric(
            lag_df[column],
            errors="coerce"
        )

    analysis_df = (
        analysis_df
        .dropna(subset=required_analysis)
        .sort_values("year")
    )

    lag_df = (
        lag_df
        .dropna(subset=required_lag)
        .sort_values("lag_years")
    )

    if analysis_df.empty or lag_df.empty:
        st.error("No valid California observations were found.")
        st.stop()

    # --------------------------------------------------------
    # 5. HISTORICAL CONTEXT
    # --------------------------------------------------------

    st.subheader("Historical Context")

    st.markdown(
        """
        California's school-entry immunization requirements
        provide policy context for examining historical
        vaccination and measles incidence patterns.

        The state's 1999 school-entry requirements included
        provisions affecting students entering seventh grade.

        **Important:** NIS-Child vaccination estimates
        represent younger children than the seventh-grade
        population affected by these requirements.
        """
    )

    # --------------------------------------------------------
    # 6. DATASET SUMMARY
    # --------------------------------------------------------

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Observed Years",
            analysis_df["year"].nunique()
        )

    with col2:
        st.metric(
            "Mean Coverage",
            f"{analysis_df['measles_coverage_pct'].mean():.2f}%"
        )

    with col3:
        st.metric(
            "Lag Periods",
            lag_df["lag_years"].nunique()
        )

    st.caption(
        "Mean coverage is an unweighted average of available "
        "annual estimates, not a population-weighted measure."
    )

    # --------------------------------------------------------
    # 7. PREPARE HISTORICAL DATA
    # --------------------------------------------------------

    early_df = analysis_df[
        analysis_df["year"].between(1995, 2002)
    ].copy()

    recent_df = analysis_df[
        analysis_df["year"].between(2016, 2017)
    ].copy()

    periods = [
        (early_df, "1995–2002", COLORS["early"]),
        (recent_df, "2016–2017", COLORS["recent"])
    ]

    # --------------------------------------------------------
    # 8. HISTORICAL TREND CHARTS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Vaccination Coverage and Disease Incidence"
    )

    st.caption(
        "The observation periods are displayed separately. "
        "Missing years are not interpolated or treated as zero."
    )

    display_period_key()

    # --------------------------------------------------------
    # CHART 1: VACCINATION COVERAGE
    # --------------------------------------------------------

    st.markdown(
        "#### California Measles Vaccination Coverage"
    )

    coverage_fig = go.Figure()

    for period_df, label, color in periods:

        coverage_fig.add_trace(
            go.Scatter(
                x=period_df["year"],
                y=period_df["measles_coverage_pct"],
                mode="lines+markers",
                name=label,
                showlegend=False,
                line=dict(
                    color=color,
                    width=3
                ),
                marker=dict(size=8),
                hovertemplate=(
                    "Year: %{x}<br>"
                    "Coverage: %{y:.2f}%"
                    "<extra></extra>"
                )
            )
        )

    coverage_fig = format_historical_chart(
        coverage_fig,
        "Vaccination Coverage (%)"
    )

    st.plotly_chart(
        coverage_fig,
        use_container_width=True,
        key="california_coverage_chart"
    )

    # --------------------------------------------------------
    # CHART 2: MEASLES INCIDENCE
    # --------------------------------------------------------

    st.markdown(
        "#### California Measles Incidence"
    )

    incidence_fig = go.Figure()

    for period_df, label, color in periods:

        incidence_fig.add_trace(
            go.Bar(
                x=period_df["year"],
                y=period_df["measles_cases_per_100k"],
                name=label,
                showlegend=False,
                marker=dict(color=color),
                width=0.75,
                hovertemplate=(
                    "Year: %{x}<br>"
                    "Incidence: %{y:.4f} per 100,000"
                    "<extra></extra>"
                )
            )
        )

    incidence_fig = format_historical_chart(
        incidence_fig,
        "Cases per 100,000 Population"
    )

    incidence_fig.update_layout(
        bargap=0.15
    )

    st.plotly_chart(
        incidence_fig,
        use_container_width=True,
        key="california_incidence_chart"
    )

    st.caption(
        "Incidence is reported as cases per 100,000 residents. "
        "These descriptive trends do not establish causation."
    )

    # --------------------------------------------------------
    # 9. INTERACTIVE TIME-LAGGED ANALYSIS
    # --------------------------------------------------------

    st.divider()

    st.subheader("Time-Lagged Association Analysis")

    st.markdown(
        """
        Explore how the reported correlation between vaccination
        coverage and measles incidence changes across lag periods.

        **0-year lag:** Coverage and incidence in the same year.

        **1-year lag:** Coverage from the preceding year
        compared with incidence in the following year.

        Longer lags represent additional calendar-year offsets.
        """
    )

    lag_options = sorted(
        lag_df["lag_years"].astype(int).unique().tolist()
    )

    selected_lag = st.select_slider(
        "Select lag period (years)",
        options=lag_options,
        value=lag_options[0]
    )

    selected_result = lag_df.loc[
        lag_df["lag_years"] == selected_lag
    ].iloc[0]

    r = float(selected_result["pearson_r"])
    p = float(selected_result["p_value"])
    n = int(selected_result["n"])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Pearson Correlation",
            f"{r:.3f}"
        )

    with col2:
        st.metric(
            "P-value",
            f"{p:.4f}"
        )

    with col3:
        st.metric(
            "Observations (n)",
            n
        )

    # --------------------------------------------------------
    # SAMPLE SIZE WARNINGS
    # --------------------------------------------------------

    if n < 5:
        st.warning(
            "Very small sample size. The correlation estimate "
            "may be highly unstable."
        )

    elif n < 10:
        st.info(
            "Limited observations are available. "
            "Interpret the estimate cautiously."
        )

    if p >= 0.05:
        st.caption(
            "The reported association does not meet "
            "the conventional p < 0.05 threshold."
        )

    else:
        st.caption(
            "The reported association meets the conventional "
            "p < 0.05 threshold. This does not establish causation."
        )

    # --------------------------------------------------------
    # DYNAMIC STATISTICAL INTERPRETATION
    # --------------------------------------------------------

    st.markdown("#### Interpretation")

    if r < 0:
        direction = "negative"
        explanation = (
            "higher coverage corresponds to lower incidence "
            "in the analyzed observations"
        )

    elif r > 0:
        direction = "positive"
        explanation = (
            "higher coverage corresponds to higher incidence "
            "in the analyzed observations"
        )

    else:
        direction = "zero"
        explanation = "no linear association was observed"

    st.write(
        f"The {selected_lag}-year lag has a {direction} "
        f"Pearson correlation (r = {r:.3f}, n = {n}). "
        f"In descriptive terms, {explanation}."
    )

    if p >= 0.05:
        st.write(
            "The reported result does not meet the conventional "
            "statistical significance threshold."
        )

    else:
        st.write(
            "The reported result meets the conventional "
            "statistical significance threshold, but causal "
            "interpretation is not justified."
        )

    st.caption(
        "The results are population-level ecological "
        "associations and may be affected by confounding, "
        "missing observations, and small sample sizes."
    )

    # --------------------------------------------------------
    # 10. CORRELATION COMPARISON
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Comparison Across All Lag Periods"
    )

    correlation_fig = go.Figure()

    correlation_colors = [
        COLORS["negative"] if value < 0
        else COLORS["positive"]
        for value in lag_df["pearson_r"]
    ]

    correlation_fig.add_trace(
        go.Bar(
            x=lag_df["lag_years"],
            y=lag_df["pearson_r"],
            marker_color=correlation_colors,
            showlegend=False,
            customdata=lag_df[
                ["p_value", "n"]
            ].to_numpy(),
            hovertemplate=(
                "Lag: %{x} years<br>"
                "Pearson r: %{y:.3f}<br>"
                "P-value: %{customdata[0]:.4f}<br>"
                "Observations: %{customdata[1]:.0f}"
                "<extra></extra>"
            )
        )
    )

    correlation_fig.update_layout(
        template="plotly_dark",
        title_text="",
        showlegend=False,
        height=440,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=55,
            r=30,
            t=25,
            b=70
        ),
        xaxis=dict(
            title_text="Lag Period (Years)",
            tickmode="linear",
            tick0=0,
            dtick=1
        ),
        yaxis=dict(
            title_text="Pearson Correlation (r)",
            range=[-1, 1],
            gridcolor="rgba(150,150,150,0.20)"
        )
    )

    correlation_fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray"
    )

    st.plotly_chart(
        correlation_fig,
        use_container_width=True,
        key="california_lag_comparison"
    )

    st.caption(
        "Correlation direction and magnitude change across "
        "lag periods. Sample sizes decrease at longer lags. "
        "None of the reported p-values is below 0.05."
    )

    # --------------------------------------------------------
    # 11. DATA TRANSPARENCY
    # --------------------------------------------------------

    st.divider()

    # --------------------------------------------------------
    # STATISTICAL VALIDATION
    # --------------------------------------------------------
    st.subheader("Statistical Validation")

    st.success(
        "The reported California Pearson correlations and "
        "p-values were independently reproduced using "
        "calendar-year matching."
    )

    st.markdown(
        """
        **Validation Approach**

        - Matched vaccination coverage in year *t* with
          measles incidence in year *t + lag*.
        - Excluded comparisons where either year was missing.
        - Preserved the gap between 2002 and 2016.
        - Verified correlation coefficients, p-values,
          and sample sizes across all six lag periods.

        **Interpretation**

        None of the six lagged associations reached the
        conventional p < 0.05 significance threshold.

        Longer lag periods contained fewer observations,
        increasing statistical uncertainty.

        **Limitation:** This validation checks the statistical
        calculations, not the original source-data extraction,
        survey weighting, or accuracy of reported incidence.
        """
    )

    st.subheader("Data and Statistical Results")

    with st.expander("View Annual California Data"):
        st.dataframe(
            analysis_df,
            use_container_width=True,
            hide_index=True
        )

    with st.expander("View All Lag Results"):
        st.dataframe(
            lag_df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 12. FLORIDA CASE STUDY
# ============================================================

elif state == "Florida":

    st.header("Florida: Measles Analysis")

    st.warning(
        "Florida analysis is in progress. "
        "Validated findings will be integrated "
        "when the data are available."
    )

    st.markdown(
        """
        The Florida case study will use the same
        framework as California:

        - Vaccination coverage trends
        - Population-normalized measles incidence
        - Time-lagged correlations
        - Statistical uncertainty
        - Historical context
        - Methodological limitations
        """
    )


# ============================================================
# 13. METHODOLOGICAL CONSIDERATIONS
# ============================================================

st.divider()

st.subheader("Methodological Considerations")

with st.expander(
    "Study Limitations",
    expanded=True
):

    st.markdown(
        """
        **Ecological Fallacy**

        Population-level relationships cannot establish
        individual-level vaccination outcomes.

        **Confounding**

        Demographic characteristics, healthcare access,
        geographic differences, surveillance practices,
        and immunization policies may influence associations.

        **Incomplete Data**

        Missing years and differences in surveyed age groups
        limit comparability.

        **Lag Structure**

        Associations must be calculated using actual
        calendar-year offsets. Gaps in the dataset cannot
        be treated as consecutive observations.

        **Statistical Uncertainty**

        Small sample sizes can produce unstable correlation
        estimates. P-values and sample sizes must be
        considered together.

        **Causation**

        Correlation does not establish that changes in
        vaccination coverage caused changes in disease incidence.
        """
    )

st.caption(
    "BIOT 670I Capstone | Group 1 | "
    "Exploratory Ecological Analysis"
)
