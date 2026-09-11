import streamlit as st

pages = {
    "Home": [
        st.Page(
            "pages/home.py",
            title="Home",
            icon="🏠",
            default=True
        )
    ],
    "Analysis": [
        st.Page(
            "pages/control.py",
            title="Control",
            icon="⚙️",
            url_path="control.py"
        ),
        st.Page(
            "pages/mmp_coverage_cases.py",
            title="MMR Coverage and Cases",
            icon="💉",
            url_path="mmp_coverage_cases.py"
        ),
    ],
    "Notebooks": [
        st.Page(
            "pages/notebooks/control_notebook.py",
            title="control_notebook.py",
            icon="📄",
            url_path="control_notebook.py"
        ),
        st.Page(
            "pages/notebooks/mmp_cases_coverage_notebook.py",
            title="mmp_cases_coverage_notebook.py",
            icon="📄",
            url_path="mmp_cases_coverage_notebook.py"
        )
    ]
}

page = st.navigation(pages)
page.run()

