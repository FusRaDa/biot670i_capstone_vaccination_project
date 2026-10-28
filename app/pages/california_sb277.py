"""California SB 277 — BIOT 670I Streamlit page.

Update the two paths under FILE PATHS to match your project.
Requires pandas, numpy, plotly, streamlit.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# FILE PATHS — EDIT THESE TWO LINES
BASE_DIR = Path(__file__).resolve().parent.parent
MEASLES_PATH = BASE_DIR / 'data' / 'measles_county.csv'
POPULATION_PATH = BASE_DIR / 'data' / 'census_population_2010_2019.csv'

YEARS = list(range(2010, 2020))


@st.cache_data
def load_data(measles_path: str, population_path: str) -> pd.DataFrame:
    cases = pd.read_csv(measles_path, encoding='latin1')
    pop = pd.read_csv(population_path, encoding='latin1', low_memory=False)
    cases.columns = cases.columns.str.strip()
    required_cases = {'Disease', 'County', 'Year', 'Count'}
    required_pop = {'SUMLEV', 'STNAME', 'CTYNAME'} | {f'POPESTIMATE{y}' for y in YEARS}
    if not required_cases.issubset(cases.columns):
        raise ValueError(f'Measles CSV missing: {sorted(required_cases - set(cases.columns))}')
    if not required_pop.issubset(pop.columns):
        raise ValueError(f'Population CSV missing: {sorted(required_pop - set(pop.columns))}')

    cases = cases[cases['Disease'].astype(str).str.strip().str.casefold() == 'measles'].copy()
    cases['year'] = pd.to_numeric(cases['Year'], errors='coerce')
    cases['measles_cases'] = pd.to_numeric(cases['Count'], errors='coerce')
    cases['county'] = cases['County'].astype(str).str.strip().str.replace(r'\s+County$', '', regex=True)
    cases = cases[cases['year'].isin(YEARS) & cases['county'].ne('California')]
    if cases.duplicated(['county', 'year']).any():
        raise ValueError('Duplicate measles records found for county/year.')

    pop = pop[(pop['STNAME'] == 'California') & (pd.to_numeric(pop['SUMLEV'], errors='coerce') == 50)].copy()
    pop['county'] = pop['CTYNAME'].astype(str).str.strip().str.replace(r'\s+County$', '', regex=True)
    pop = pop.melt(id_vars=['county'], value_vars=[f'POPESTIMATE{y}' for y in YEARS],
                   var_name='year', value_name='population')
    pop['year'] = pop['year'].str.extract(r'(\d{4})').astype(int)
    pop['population'] = pd.to_numeric(pop['population'], errors='coerce')
    if pop.duplicated(['county', 'year']).any():
        raise ValueError('Duplicate Census population records found for county/year.')

    panel = pop.merge(cases[['county', 'year', 'measles_cases']], on=['county', 'year'], how='left', validate='one_to_one')
    panel['measles_per_100k'] = np.where(panel['population'] > 0,
                                        panel['measles_cases'] / panel['population'] * 100_000, np.nan)
    return panel.sort_values(['county', 'year'])

st.title('California SB 277 Policy Analysis')
st.caption('California • 2010–2019 • Vaccination exemptions and measles incidence')

try:
    panel = load_data(str(MEASLES_PATH), str(POPULATION_PATH))
except (OSError, ValueError, pd.errors.ParserError) as exc:
    st.error(f'Could not load the two source CSVs: {exc}')
    st.stop()

state = (panel.groupby('year', as_index=False)
         .agg(measles_cases=('measles_cases', lambda x: x.sum(min_count=1)),
              population=('population', 'sum')))
state['measles_per_100k'] = 100_000 * state['measles_cases'] / state['population']

# Statewide enrollment-weighted kindergarten exemption rates reported in
# California_SB277_Summary.ipynb; neither supplied CSV contains these data.
exemptions = pd.DataFrame({
    'year': YEARS,
    'pbe_pct': [np.nan, np.nan, np.nan, 3.094, 2.491, 2.331, 1.405, 0.907, np.nan, np.nan],
    'medical_pct': [np.nan, np.nan, np.nan, 0.185, 0.190, 0.167, 1.327, 1.508, 1.633, 1.641],
})
state = state.merge(exemptions, on='year', how='left')

st.markdown('''
### Background
California Senate Bill 277 (SB 277) was enacted in 2015 and implemented in 2016.
It eliminated personal-belief exemptions from required school vaccinations while
retaining medical exemptions.

**Research question:** How did vaccine exemptions and measles incidence change
around the implementation of SB 277?
''')

pre = state[state['year'].between(2013, 2015)]
post = state[state['year'].between(2016, 2019)]
pre_pbe = pre['pbe_pct'].mean()
post_pbe = post['pbe_pct'].mean()
pre_med = pre['medical_pct'].mean()
post_med = post['medical_pct'].mean()
pre_inc = pre['measles_per_100k'].mean()
post_inc = post['measles_per_100k'].mean()

st.subheader('Key findings (statewide)')
a, b, c = st.columns(3)
a.metric('Personal-belief exemptions', f'{post_pbe:.2f}%', f'{post_pbe - pre_pbe:+.2f} pp')
b.metric('Medical exemptions', f'{post_med:.2f}%', f'{post_med - pre_med:+.2f} pp')
c.metric('Measles incidence', f'{post_inc:.3f} / 100k', f'{post_inc - pre_inc:+.3f} / 100k')
st.caption('Pre-policy: 2013–2015; post-policy: 2016–2019. Personal-belief exemptions have post-policy observations only for 2016–2017. Descriptive comparisons do not establish causality.')

st.subheader('Explore annual trends')
county = st.selectbox('Measles incidence geography', ['California (statewide)'] + sorted(panel['county'].unique().tolist()))
view = state if county == 'California (statewide)' else panel[panel['county'] == county].sort_values('year')

def format_chart(fig, ytitle):
    fig.add_vline(x=2016, line_dash='dash', line_color='gray',
                  annotation_text='SB 277 implemented', annotation_position='top left')
    fig.update_layout(height=430, hovermode='x unified', yaxis_title=ytitle,
                      xaxis=dict(title='Year', dtick=1, range=[2009.7, 2019.3]),
                      legend=dict(orientation='h', y=1.15),
                      margin=dict(l=15, r=15, t=60, b=15))
    return fig

st.markdown('#### Kindergarten exemption rates — California statewide')
fig1 = go.Figure()
for field, label, color in [
    ('pbe_pct', 'Personal-belief exemptions', '#d97706'),
    ('medical_pct', 'Medical exemptions', '#2563eb'),
]:
    fig1.add_trace(go.Scatter(x=state['year'], y=state[field], name=label,
                              mode='lines+markers', connectgaps=False,
                              line=dict(color=color, width=3), marker=dict(size=8),
                              hovertemplate='%{y:.3f}%<extra>%{fullData.name}</extra>'))
st.plotly_chart(format_chart(fig1, 'Exemption rate (%)'), width='stretch')
st.caption('Statewide exemption values are from the classmate’s notebook, not the two CSVs. Missing years are not filled in. The county selector does not affect this chart.')

st.markdown(f'#### Measles incidence — {county}')
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=view['year'], y=view['measles_per_100k'],
                          name='Measles incidence', mode='lines+markers',
                          line=dict(color='#7c3aed', width=3), marker=dict(size=8),
                          connectgaps=False, hovertemplate='%{y:.3f} per 100k<extra></extra>'))
st.plotly_chart(format_chart(fig2, 'Cases per 100,000 residents'), width='stretch')
st.caption('Incidence is calculated from the two supplied CSVs. Statewide cases sum only the 58 counties, excluding the separate California aggregate record.')

with st.expander('View annual data'):
    cols = ['year', 'measles_cases', 'population', 'measles_per_100k']
    if county == 'California (statewide)':
        cols += ['pbe_pct', 'medical_pct']
    st.dataframe(view[cols].style.format(precision=3, na_rep='—'),
                 hide_index=True, width='stretch')

st.subheader('Original county-level correlation analysis')
corr = pd.DataFrame([
    ['MMR coverage', '2019', 57, -0.0767, 0.5708],
    ['MMR coverage (1-year lag)', '—', 0, np.nan, np.nan],
    ['Personal-belief exemptions', '2013–2015', 172, -0.0643, 0.4017],
    ['Personal-belief exemptions (1-year lag)', '2014–2015', 115, -0.1416, 0.1311],
    ['Medical exemptions', '2013–2019', 398, 0.0236, 0.6387],
    ['Medical exemptions (1-year lag)', '2014–2019', 341, 0.0394, 0.4687],
], columns=['Exposure', 'Years', 'N', 'Pearson r', 'p-value'])
st.dataframe(corr.style.format({'Pearson r': '{:.3f}', 'p-value': '{:.4f}'}, na_rep='—'),
             hide_index=True, width='stretch')
st.caption('Original classmate notebook results; not recalculated from these two CSVs or filtered by the county selector. Lag 1 compares prior-year exposure with current-year incidence.')

st.subheader('Interpretation and limitations')
with st.expander('Interpretation', expanded=True):
    st.write('Personal-belief exemptions decreased after SB 277 while medical exemptions increased. The statewide average measles incidence was lower in the post-policy period. Weak county-level correlations do not establish a causal effect of the law.')
with st.expander('Limitations'):
    st.write('Historical MMR coverage is largely unavailable; personal-belief exemption observations end in 2017. Measles is rare, and incidence can reflect travel-related introductions, local susceptible clusters, other policies, and surveillance differences. County-level associations are ecological and not causal.')

st.markdown('### Data sources')
st.markdown('''
- California Department of Public Health: `measles_county.csv` (reported measles cases)
- U.S. Census Bureau: `census_population_2010_2019.csv` (county population estimates)
- BIOT 670I group analysis: `California_SB277_Summary.ipynb` (statewide exemption values and original correlations)
''')