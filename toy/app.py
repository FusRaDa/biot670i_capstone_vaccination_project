import streamlit as st

# Add a header title
st.title("My First Streamlit App")

# Add an interactive slider widget
number = st.slider("Select a value", 0, 100, 50)

# Display dynamic results text
st.write(f"The square of {number} is {number ** 2}")
