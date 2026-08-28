import streamlit as st

st.set_page_config(page_title="Project Tycho Level 1 Control", page_icon="⚙️")

st.markdown("Project Tycho Measles Control: 1931 to 1992")
st.sidebar.header("Project Tycho Measles Control")
st.write(
    """
    ### Positive Control

    Reproduce the well-established collapse in **measles incidence after the 1963 vaccine introduction** using Project Tycho data.

    Article: https://academic.oup.com/ofid/article/5/7/ofy137/5039595

    If the analysis pipeline cannot recover this established historical pattern, it suggests a problem with the data processing or analysis.
    """
)



st.write(
    """
    ### Placebo Check

    Correlate **vaccination coverage** with a **non-vaccine-preventable health outcome**.

    A strong association with an unrelated outcome may indicate **confounding, spurious correlation, or problems in the analysis pipeline**.
    """
)

