# folder for work done by Moira Overly
BIOT 670I Capstone — Dashboard Development Contributions
Contributor: Moira Overly
Project: Vaccination Coverage and Disease Incidence (Measles, Mumps, Pertussis)
Team: BIOT 670I Group 1 (2026)
Primary responsibility: Streamlit dashboard implementation, visualization, state case studies, integration, and data-quality communication.
This notebook is a concise, reproducible account of my dashboard contributions. It does not claim authorship of source surveillance datasets or statistical analyses produced by other team members.


1. Research purpose and my role
Cell 2 of 11

1. Research purpose and my role
The group built an ecological exploration tool connecting vaccination coverage to reported disease incidence by state and year. Its purpose is to expose patterns and uncertainty, not establish that coverage changes caused outbreaks.
I implemented and refined the user-facing Streamlit experience, including:
- California measles case-study charts and interactive 0–5-year lag-results display.
- Florida measles case-study integration using teammate-provided analysis CSVs.
- State-specific data completeness, lag-pair counts, caveats, and warnings about small samples.
- A distinct MMP master-data explorer for California and Florida covering measles, mumps, and pertussis.
- Usability improvements: readable 60° year labels, separation of missing-year segments, and Plotly title/legend corrections.
- Version control through Git feature branches and pull requests for review.
Attribution: The master data and Florida lag-analysis outputs were created/compiled by the wider group; my contribution here is their dashboard integration and visualization.


2. Files and contributions
Cell 3 of 11

2. Files and contributions
Project file	Contribution
app/pages/state_case_studies.py	California and Florida measles case studies, interactive lag statistics, completeness checks, explanations
app/pages/mmp_master_explorer.py	Descriptive MMP explorer with disease and state filters and side-by-side trends
app/app.py	Registered the master-explorer page in Streamlit navigation
app/data/florida_measles_analysis.csv	Integrated the team-produced Florida observations into the app data directory
app/data/florida_measles_lag_results.csv	Integrated the team-produced lag-results CSV into the app data directory


Reproducibility note: This notebook expects to be saved under overly_notebooks/ in the group repository, with the CSV files under app/data/.


Code cell 4
Cell 4 of 11

from pathlib import Path
import pandas as pd

# Works from either the Jupyter project root or the overly_notebooks folder.
cwd = Path.cwd()
ROOT = cwd if (cwd / "app" / "data").exists() else cwd.parent
DATA = ROOT / "app" / "data"
print("Project root:", ROOT)
print("Master data available:", (DATA / "cases_coverage_ms.csv").exists())
print("CA and FL lag datasets:", [(s, (DATA / f"{s}_measles_lag_results.csv").exists()) for s in ["california", "florida"]])

3. Master-data explorer: descriptive coverage and incidence
Cell 5 of 11

3. Master-data explorer: descriptive coverage and incidence
This component enables state and disease selection for all three MMP diseases. Cases are displayed as incidence per 100,000, allowing comparisons between differently sized states. The master-data explorer is descriptive and does not calculate lagged correlations.


Code cell 6
Cell 6 of 11

master_path = DATA / "cases_coverage_ms.csv"
if master_path.exists():
    master = pd.read_csv(master_path)
    print("Shape:", master.shape)
    print("Columns:", master.columns.tolist())
    display(master.head(5))
else:
    print("Master CSV not found here. Run notebook from the group repository.")

4. State case studies: lag analysis display
Cell 7 of 11

4. State case studies: lag analysis display
The case-study page consumes precomputed California and Florida measles lag-results CSVs. For each 0–5-year lag, it presents Pearson's r, a p-value, the number of usable pairs, and interpretive warnings. I added calendar-year observation-pair checks as a transparency tool; matching pair counts alone does not validate the statistical model.


Code cell 8
Cell 8 of 11

for state in ["california", "florida"]:
    lag_path = DATA / f"{state}_measles_lag_results.csv"
    if lag_path.exists():
        df = pd.read_csv(lag_path)
        fields = [c for c in ["lag_years", "pearson_r", "p_value", "n"] if c in df.columns]
        print(f"\n{state.title()} reported lag outputs:")
        display(df[fields].sort_values("lag_years") if "lag_years" in fields else df.head())
    else:
        print(f"{lag_path.name} missing; no results invented.")

5. Data quality and interpretive safeguards
Cell 9 of 11

5. Data quality and interpretive safeguards
- Year completeness counts require both coverage and incidence to be present.
- Missing disease-incidence observations are not zero-filled or interpolated.
- Charts avoid implying continuous observations where years are absent.
- Reported lag sample sizes are shown alongside available calendar-year pairs.
- Small sample warnings explain how extreme Pearson coefficients can be unstable.
- NIS-Child estimates measure a different sampled population from state-wide surveillance cases; survey estimation/weighting should be checked against team methodology.
- Ecological relationships do not establish individual vaccine effects, and the analyses may have unmeasured confounding.


6. Development workflow and supporting evidence
Cell 10 of 11

6. Development workflow and supporting evidence
1. Built a California measles Streamlit case-study page and iteratively corrected chart labels and interpretation.
2. Added state-specific observation-quality reporting and pair-count checks.
3. Integrated Florida's team-produced measles observations and lag results using the shared case-study layout.
4. Built the separate MMP Explorer so that all three diseases appear without conflating descriptive results with measles-only lag analyses.
5. Updated Streamlit navigation and submitted changes on feature branches for team review.
Supporting evidence (replace with actual final URLs and screenshots when available):
- Group repository
- Live group application
- Dashboard integration commit e5ab01b on overly-final-integration (verify availability on GitHub)
- Case-study PR #22; Data Quality PR #23 (see GitHub history)
Screenshots can be placed in overly_notebooks/images/ and linked here after confirming they show the final reviewed implementation.


7. Key takeaway
Cell 11 of 11

7. Key takeaway
My contribution translated the group's surveillance datasets and precomputed measles analyses into a navigable, interactive dashboard. The design makes data completeness, comparison scope, small-sample uncertainty, and limits of ecological inference visible to users. Broader MMP trends are presented separately from narrower California/Florida measles lag analyses.