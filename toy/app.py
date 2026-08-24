import streamlit as st
import seaborn as sns
import plotly.express as px
import pandas as pd


# Add a header title
st.title("BIOT 670I Group 1 - Toy Data")
st.subheader("Restaurant Tips Analysis")

# Data on restaurant tips
df = sns.load_dataset('tips')


# extract columns
day = df['day']
total_bill = df['total_bill']
time = df['time']
tip = df['tip']
sex = df['sex']

# Who tips more?
day_tip_sex_gr = px.histogram(df, x=day, y=tip,
             color=sex, barmode='group',
             color_discrete_map={"Male": "blue", "Female": "red"},
             title="Who gives the most tips?",
             height=400)

day_tip_sex_gr.update_yaxes(title_text="Tip Amount ($)")
day_tip_sex_gr.update_xaxes(title_text="Day")


# What day makes the most revenue?
day_total_time_gr = px.histogram(df, x=day, y=total_bill,
             color=time, barmode='group',
             color_discrete_map={"Dinner": "blue", "Lunch": "yellow"},
             title="What days make the most revenue?",
             height=400)

day_total_time_gr.update_yaxes(title_text="Total Bill ($)")
day_total_time_gr.update_xaxes(title_text="Day")

st.plotly_chart(day_tip_sex_gr)
st.plotly_chart(day_total_time_gr)
