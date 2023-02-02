import streamlit as st
import pandas as pd
import requests
st.set_page_config(layout="wide")
st.title("Scoresheet GE15")

folder_path = "https://github.com/AmaniAli95/streamlit-GPS-ethnic/tree/main/scoresheets-ge15-pdf"

response = requests.get(folder_path)
if response.status_code != 200:
    st.write(f"Error: Response status code is {response.status_code}")
else:
    st.write(response.content)
pdf_files = [f for f in response.json() if f["name"].endswith(".pdf")]

st.sidebar.header("File List")

filename = st.sidebar.radio("Select a file:", [pdf_file["name"] for pdf_file in pdf_files])
st.sidebar.write(f"You selected: {filename}")
