import streamlit as st
import pandas as pd
import re
import plotly.graph_objs as go
import textwrap
import requests
import os

#github use
url = "https://github.com/AmaniAli95/streamlit-GPS-ethnic/raw/main/demographic.csv"
df = pd.read_csv(url)

st.title("Nomination by Ethnic")
#df = pd.read_csv('/Users/fatinamanimohdali/Desktop/MAVEN2023/PRU2022/demographic.csv')

# Dropdown
def filter_data(level):
    return df[df['P_name'] == level]
level = st.selectbox('Select Parliament:', df['P_name'].dropna().unique().tolist())
filtered_df = filter_data(level)
d_name = st.selectbox('Select District:', filtered_df['D_name'].dropna().unique().tolist())

#Jumlah pengundi berdaftar
st.markdown('### Jumlah Pengundi Berdaftar')
selected_rows = df[df['D_name'] == d_name]
ethnic_columns = [col for col in df.columns if col.startswith('ethnic|')]
renamed_columns = {col: col.replace('ethnic|', '') for col in ethnic_columns}
selected_rows.rename(columns=renamed_columns, inplace=True)
total = selected_rows[list(renamed_columns.values())].sum(axis=1)
total_df = pd.DataFrame({'Total': total})
html = (
    pd.concat([selected_rows[list(renamed_columns.values())], total_df], axis=1)
    .style.set_properties(**{'text-align': 'center'})
    .hide_index()
    .render()
)
st.write(html, unsafe_allow_html=True)

#Slider Jumlah Keluar Mengundi
st.markdown('### ')
st.markdown('### Jumlah Keluar Mengundi')

#split to two columns
col1, col2 = st.columns(2)
with col1:
    default_value = 72
    slider_range = (0, 100)
    slider_value = st.slider('Select percentage of keluar mengundi:', slider_range[0], slider_range[1],
                             default_value)
def calculate_values(row):
    return [slider_value * x / 100 for x in row]

with col2:
    values = selected_rows[list(renamed_columns.values())].apply(calculate_values, axis=1)
    for i, column_name in enumerate(renamed_columns.values()):
        st.markdown(f"##### {column_name}: {str(values.values[0][i])}")

