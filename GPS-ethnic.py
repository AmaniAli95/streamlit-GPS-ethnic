import streamlit as st
import pandas as pd
import requests
import PyPDF2
from PyPDF2 import PdfReader
import base64

import subprocess
import tempfile

st.set_page_config(layout="wide")
st.title("Scoresheet GE15")

#password
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    folder_path = "https://api.github.com/repos/AmaniAli95/streamlit-GPS-ethnic/contents/scoresheets-ge15-pdf"
    response = requests.get(folder_path)

    pdf_files = [f for f in response.json() if f["name"].endswith(".pdf")]
    st.sidebar.header("File List")
    filename = st.sidebar.radio("Select a file:", [pdf_file["name"].rstrip(".pdf") for pdf_file in pdf_files])

#    def show_pdf(file_path):
#        with open(file_path,"rb") as f:
#            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
#        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
#        st.markdown(pdf_display, unsafe_allow_html=True)

#    pdf_url = [pdf_file["download_url"] for pdf_file in pdf_files if pdf_file["name"] == filename + ".pdf"][0]
#    response = requests.get(pdf_url)
#    with open("temp.pdf", "wb") as f:
#        f.write(response.content)
#    show_pdf("temp.pdf")

    def pdf_to_image(pdf_file, page_number=0, dpi=200):
        with tempfile.NamedTemporaryFile(suffix=".png") as img:
            subprocess.run(["convert", "-density", str(dpi), f"{pdf_file}[{page_number}]", img.name])
            return img.name
    
    pdf_url = [pdf_file["download_url"] for pdf_file in pdf_files if pdf_file["name"] == filename + ".pdf"][0]
    response = requests.get(pdf_url)
    with open("temp.pdf", "wb") as f:
        f.write(response.content)
        
    # convert the first page of the PDF file to image
    image_file = pdf_to_image("temp.pdf")

    # display the image
    st.image(image_file, width=600)
