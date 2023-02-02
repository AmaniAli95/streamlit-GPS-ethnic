import streamlit as st
import pandas as pd
import requests
st.set_page_config(layout="wide")
st.title("Scoresheet GE15")

folder_path = "https://github.com/AmaniAli95/streamlit-GPS-ethnic/tree/main/scoresheets-ge15-pdf"
filenames = [f for f in folder_path if f.endswith(".pdf")]

st.header("File List")
for filename in filenames:
    st.sidebar.radio(filename)
