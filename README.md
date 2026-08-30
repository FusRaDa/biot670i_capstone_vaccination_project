# This is the repository for BIOT670I Group 1
- Bakry, Heba
- Bukirwa, Gloria
- Overly, Moira
- Perin, Kalkidan
- Rada, Matthew


### Documents
- Project Outline
    - https://docs.google.com/document/d/16FiXpB9fuYY9Yqj8b4IVwNM_ZnQetMudPUvE6nPitbA/edit?usp=sharing


### Tech Stack
- pandas
- statsmodels
- Streamlit
- Plotly


### Setup
1. Clone repo to local computer
    - git clone https://github.com/FusRaDa/biot670i_capstone_vaccination_project.git
    - cd to biot670i_capstone_vaccination_project/

2. Create python virtual environment (development - Python 3.13.9)
    - ```python -m venv .venv```
    - ```source .venv/bin/activate```
    - these commands will slighty differ based on your system and method of installation

3. Install dependancies - CHECK THAT YOU HAVE ACTIVATED VIRTUAL ENVIRONMENT
    - ```pip install -r requirements.txt```

4. Run toy data into streamlit
    - ```streamlit run toy/app.py```

5. Create your own branch from main
    - ```git switch -c YOUR_LAST_NAME```
    - check current branch ```git branch```


### Files & Directories
- toy/ - holds prrof of concept in terms of using the tech stack.
    - run ```streamlit run toy/app.py``` to see proof of concept


### How to deploy in Streamlit
- visit and login to: https://streamlit.io/cloud
- Add app > find repo > set branch to main > app file path: ```app/app.py```


### Live app
- https://biot670i-group1.streamlit.app/