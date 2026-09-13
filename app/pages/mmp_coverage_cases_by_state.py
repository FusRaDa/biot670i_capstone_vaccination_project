import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Measles, Mumps, Pertussis Cases & Coverage", page_icon="🇺🇸")

st.markdown("Measles, Mumps, Pertussis Cases & Coverage Per State: 1995 - 2017")
st.sidebar.header("Measles, Mumps, Pertussis Cases & Coverage Per State")

st.write(
    """
    ### Suggested States for Analysis

    **California** is the strongest overall choice. The state experienced major pertussis epidemics in 2010 and 2014, followed by the passage of Senate Bill 277 in 2015, which eliminated personal-belief exemptions for required school vaccinations. This supports both outbreak and policy analysis. See [California SB 277](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201520160SB277).

    **Minnesota** experienced a major measles outbreak in 2017 associated with reduced MMR vaccination in a localized community. Because the event occurred during the final year of your coverage and CDC measles datasets, Minnesota provides one of the clearest comparisons in your study. See the [CDC outbreak report](https://stacks.cdc.gov/view/cdc/47978).

    **Ohio** experienced a large measles outbreak in an underimmunized Amish community in 2014. It is useful for showing how localized vaccination gaps can produce substantial outbreaks even when statewide coverage appears high.

    **Washington** declared a pertussis epidemic in 2012 after reported cases increased sharply. This event falls directly within the years covered by both your pertussis and vaccination datasets, making Washington one of the best options for a state-level time-series analysis. See the [Washington Department of Health](https://doh.wa.gov/you-and-your-family/illness-and-disease-z/pertussis-whooping-cough/pertussis-notifiable-condition).

    **New York** experienced a large mumps outbreak beginning in 2009, particularly within close-knit communities in New York City and surrounding areas. It provides a useful example of an outbreak occurring despite relatively high vaccination coverage.

    **Arkansas** experienced a large mumps outbreak during 2016–2017. Because these years are present in your mumps case series, Arkansas is especially useful for examining whether statewide coverage measures concealed vulnerable communities.

    For the cleanest analysis using the data you already have, I would prioritize:

    1. **California — pertussis, 2010 and 2014**
    2. **Washington — pertussis, 2012**
    3. **Minnesota — measles, 2017**
    4. **Arkansas — mumps, 2016–2017**

    Ohio and New York are historically valuable, but their major events fall inside gaps in your current Tycho measles or mumps series, so they would require supplemental CDC case data.
    """
)

cases_df = pd.read_csv('app/data/tycho_cases.csv')
coverage_df = pd.read_csv('app/data/nis_vacc_coverage.csv')
yearly_coverage_cases_df = pd.merge(cases_df, coverage_df, on=['year', 'state'])


selected_state = st.selectbox(
    "Select a state",
    sorted(yearly_coverage_cases_df["state"].dropna().unique())
)

filtered_df = yearly_coverage_cases_df[yearly_coverage_cases_df["state"] == selected_state]


def graph_coverage_cases_df(df):

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
                x=df["year"],
                y=df[f"{disease}_cases"],
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
                x=df["year"],
                y=df[f"{disease}_coverage_pct"],
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
        title=f"Annual Vaccination Coverage and Reported Cases",
        template="plotly_white",
        height=900,
        hovermode="x unified",
        legend_title="Measure",
        bargap=0.20
    )

    return fig


fig = graph_coverage_cases_df(filtered_df)
st.plotly_chart(fig, width="stretch")

