import streamlit as st
import pandas as pd
import requests
import PyPDF2
from PyPDF2 import PdfReader
st.set_page_config(layout="wide")
st.title("Scoresheet GE15")

folder_path = "https://api.github.com/repos/AmaniAli95/streamlit-GPS-ethnic/contents/scoresheets-ge15-pdf"
response = requests.get(folder_path)

pdf_files = [f for f in response.json() if f["name"].endswith(".pdf")]
st.sidebar.header("File List")
filename = st.sidebar.radio("Select a file:", [pdf_file["name"] for pdf_file in pdf_files])
st.write(f"You selected: {filename}")

pdf_url = [pdf_file["download_url"] for pdf_file in pdf_files if pdf_file["name"] == filename][0]
pdf_content = requests.get(pdf_url).content
with open("temp.pdf", "wb") as f:
    f.write(pdf_content)
pdf_file = PyPDF2.PdfReader(open("temp.pdf", "rb"))
st.write("Content of the PDF file:")
for page in pdf_file.pages:
    st.write(page.extract_text())
