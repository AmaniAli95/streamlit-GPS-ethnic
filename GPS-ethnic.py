import streamlit as st
import pandas as pd
import requests
st.set_page_config(layout="wide")
st.title("Scoresheet GE15")

folder_path = "https://github.com/AmaniAli95/streamlit-GPS-ethnic/tree/main/scoresheets-ge15-pdf"
response = requests.get(folder_path)
pdf_files = [f for f in response.json() if f["name"].endswith(".pdf")]

st.header("File List")
for filename in filenames:
    st.sidebar.radio(filename)
