import streamlit as st
import pandas as pd
import requests
from google.oauth2 import service_account
from gsheetsdb import connect
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
st.set_page_config(layout="wide")

url = "https://github.com/AmaniAli95/streamlit-GPS-ethnic/raw/main/demographic.csv"
df = pd.read_csv(url)
age_columns = [col for col in df.columns if col.startswith('age_group|')]
for col in age_columns:
    df[col] = df[col].astype(str)
    df[col] = df[col].apply(lambda x: x.replace(',', ''))
    df[col] = df[col].astype(int)

st.title("GPS Votes Simulation")

# Create a sidebar
#st.sidebar.title("Forecast Category")
#chart_type = st.sidebar.button("", ["Ethnics", "Age"])
chart_type = st.sidebar.radio('Select Category',('Ethnics', 'Age'))


# Dropdown
def filter_data(level):
    return df[df['P'] == level]

df['P'] = df.apply(lambda row: row['P_code'] + ' ' + row['P_name'], axis=1)
df['D'] = df.apply(lambda row: row['D_code'] + ' ' + row['D_name'], axis=1)
level = st.selectbox('Select Parliament:', df['P'].dropna().unique().tolist())
filtered_df = filter_data(level)
d_name = st.selectbox('Select District:', filtered_df['D'].dropna().unique().tolist())

#Number of Registered Voters
def to_percentage(val):
    return '{:.2f}%'.format(val)

if chart_type == "Age":
    st.markdown("### Number of Registered Voters")
    selected_rows = df[df['D'] == d_name]
    age_columns = [col for col in df.columns if col.startswith('age_group|')]
    renamed_columns = {col: col.replace('age_group|', '').replace('_', ' ').
                       replace('o90', 'Over 90 y/o').replace('b20', 'Below 20 y/o').
                       replace('20s', '20 - y/o').replace('30s', '30 - 39 y/o').
                       replace('40s', '40 - 49 y/o').replace('50s', '50 - y/o').
                       replace('60s', '60 - 69 y/os').replace('70s', '70 - 79 y/o').
                       replace('80s', '80 - 89 y/o') for col in age_columns}
    selected_rows.rename(columns=renamed_columns, inplace=True)
    selected_rows[list(renamed_columns.values())] = selected_rows[list(renamed_columns.values())].apply(pd.to_numeric, errors='coerce')
    selected_rows[list(renamed_columns.values())].fillna(0, inplace=True)
    total = selected_rows[list(renamed_columns.values())].astype(int).sum(axis=1)
    total_df = pd.DataFrame({'Total': total})
    dfnew = (pd.concat([selected_rows[list(renamed_columns.values())], total_df], axis=1))
    percentages = dfnew[list(renamed_columns.values())].div(total, axis=0).mul(100)
    dfnew = dfnew.append(percentages.applymap(to_percentage), ignore_index=True)
    dfnew.insert(0, 'Age Group', ['Voters','Percentage'])
    dfnew.at[1, dfnew.columns[10]] = 100
    dfnew['Total'] = dfnew['Total'].astype(int)
    html = (
        dfnew
        .style.set_properties(**{'text-align': 'center'})
        .hide_index()
        .render()
    )
    st.write(html, unsafe_allow_html=True)

    #Slider values
    st.markdown('### ')
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    with col1:
        st.markdown("#### Age Group")
        st.markdown(f"### ")
        st.markdown(f"### ")
        for i, column_name in enumerate(renamed_columns.values()):
            st.markdown(f"### ")
            st.markdown(f"##### {column_name}")
            st.markdown(f"# ")
    with col2:
        st.markdown("#### Turnout forecast")
        st.markdown(f"# ")
        slider_values1 = {}
        for i, column_name in enumerate(renamed_columns.values()):
            if column_name not in st.session_state:
                st.session_state[column_name] = 72
            slider_values1[column_name] = st.slider("", 0, 100, st.session_state[column_name], key=column_name, format='%d%%')
    with col3:
        st.markdown("#### GPS support forecast")
        st.markdown(f"# ")
        slider_values = {}
        for i, column_name in enumerate(renamed_columns.values()):
            key = f"slider_col3_{column_name}"
            if key not in st.session_state:
                st.session_state[key] = 70
            slider_values[column_name] = st.slider("", 0, 100, st.session_state[key], key=key, format='%d%%')
    with col4:
        all_data = {}
        GPSvote = 0
        st.markdown("#### Vote count forecast")
        st.markdown(f"###### ")
        st.markdown(f"###### ")
        st.markdown(f"###### ")
        for i, column_name in enumerate(renamed_columns.values()):
            value = int((dfnew[list(renamed_columns.values())]).values[0][i] * slider_values1[column_name]/100 * slider_values[column_name]/100)
            st.markdown(f"##### &emsp;&emsp;&emsp;&emsp;{value}")
            st.markdown(f"## ")
            st.markdown(f"###### ")
            st.markdown(f"###### ")
            all_data[f"{column_name} | Pct Turnout Forecast"] = slider_values1[column_name]
            all_data[f"{column_name} | Pct GPS Support_Forecast"] = slider_values[column_name]
            all_data[f"{column_name} | Vote Count Forecast"] = value
            GPSvote += value
    nonGPSvote = total.values - GPSvote
    GPSwin = int((total.values)[0]/2 + 1)
    GPSwin23 = int((total.values)[0]/3 + GPSwin)
    remGPSvote = abs(GPSvote - GPSwin)
    st.markdown(f"### In order for GPS to earn a simple majority, it needs {GPSwin} support")
    st.markdown(f"### Currently, it expected to garner {GPSvote} support")
    if GPSvote >= GPSwin23:
        st.markdown("<h2 style='color: green; animation: pulse 3s infinite'>GPS is Winning. It forecast to win 2/3 votes</h2>",
                    unsafe_allow_html=True)
    elif GPSvote > nonGPSvote:
        st.markdown("<h2 style='color: green; animation: pulse 3s infinite'>GPS is Winning</h2>",
                    unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color: red; animation: pulse 3s infinite'>GPS is Losing - it needs {} support to win</h2>".format(remGPSvote),
                    unsafe_allow_html=True)

elif chart_type == "Ethnics":
    st.markdown("### Number of Registered Voters")
    selected_rows = df[df['D'] == d_name]
    ethnic_columns = [col for col in df.columns if col.startswith('ethnic|')]
    renamed_columns = {col: col.replace('ethnic|', '').replace('_', ' ').title() for col in ethnic_columns}
    selected_rows.rename(columns=renamed_columns, inplace=True)
    total = selected_rows[list(renamed_columns.values())].sum(axis=1)
    total_df = pd.DataFrame({'Total': total})
    dfnew = (pd.concat([selected_rows[list(renamed_columns.values())], total_df], axis=1))
    percentages = dfnew[list(renamed_columns.values())].div(total, axis=0).mul(100)
    dfnew = dfnew.append(percentages.applymap(to_percentage), ignore_index=True)
    dfnew.insert(0, 'Ethnic', ['Voters','Percentage'])
    dfnew.at[1, dfnew.columns[7]] = 100
    dfnew['Total'] = dfnew['Total'].astype(int)
    html = (
        dfnew
        .style.set_properties(**{'text-align': 'center'})
        .hide_index()
        .render()
    )
    st.write(html, unsafe_allow_html=True)

    #Slider values
    st.markdown('### ')
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    with col1:
        st.markdown("#### Ethnic")
        st.markdown(f"### ")
        st.markdown(f"### ")
        for i, column_name in enumerate(renamed_columns.values()):
            st.markdown(f"### ")
            st.markdown(f"##### {column_name}")
            st.markdown(f"# ")
    with col2:
        st.markdown("#### Turnout forecast")
        st.markdown(f"# ")
        slider_values1 = {}
        for i, column_name in enumerate(renamed_columns.values()):
            if column_name not in st.session_state:
                st.session_state[column_name] = 72
            slider_values1[column_name] = st.slider("", 0, 100, st.session_state[column_name], key=column_name, format='%d%%')
    with col3:
        st.markdown("#### GPS support forecast")
        st.markdown(f"# ")
        slider_values = {}
        for i, column_name in enumerate(renamed_columns.values()):
            key = f"slider_col3_{column_name}"
            if key not in st.session_state:
                st.session_state[key] = 70
            slider_values[column_name] = st.slider("", 0, 100, st.session_state[key], key=key, format='%d%%')
    with col4:
        all_data = {}
        GPSvote = 0
        st.markdown("#### Vote count forecast")
        st.markdown(f"###### ")
        st.markdown(f"###### ")
        st.markdown(f"###### ")
        for i, column_name in enumerate(renamed_columns.values()):
            value = int((dfnew[list(renamed_columns.values())]).values[0][i] * slider_values1[column_name]/100 * slider_values[column_name]/100)
            st.markdown(f"##### &emsp;&emsp;&emsp;&emsp;{value}")
            st.markdown(f"## ")
            st.markdown(f"###### ")
            st.markdown(f"###### ")
            all_data[f"{column_name} | Pct Turnout Forecast"] = slider_values1[column_name]
            all_data[f"{column_name} | Pct GPS Support_Forecast"] = slider_values[column_name]
            all_data[f"{column_name} | Vote Count Forecast"] = value
            GPSvote += value
    nonGPSvote = total.values - GPSvote
    GPSwin = int((total.values)[0]/2 + 1)
    GPSwin23 = int((total.values)[0]/3 + GPSwin)
    remGPSvote = abs(GPSvote - GPSwin)
    st.markdown(f"### In order for GPS to earn a simple majority, it needs {GPSwin} support")
    st.markdown(f"### Currently, it expected to garner {GPSvote} support")
    if GPSvote >= GPSwin23:
        result = "<h2 style='color: green; animation: pulse 3s infinite'>GPS is Winning. It forecast to win 2/3 votes</h2>"
    elif GPSvote > nonGPSvote:
        result = "<h2 style='color: green; animation: pulse 3s infinite'>GPS is Winning</h2>"
    else:
        result = "<h2 style='color: red; animation: pulse 3s infinite'>GPS is Losing - it needs {} support to win</h2>".format(remGPSvote)
    st.markdown(result, unsafe_allow_html=True)
    soup = BeautifulSoup(result, 'html.parser')
    text_result = soup.h2.text
        
def _update_slider():
    description
    for i, column_name in enumerate(renamed_columns.values()):
        if column_name not in st.session_state:
           st.session_state[column_name] = 72
        st.session_state[column_name] = 72
    for i, column_name in enumerate(renamed_columns.values()):
        key = f"slider_col3_{column_name}"
        if key not in st.session_state:
           st.session_state[key] = 70
        st.session_state[key] = 70   
    #st.experimental_rerun()   
st.button("Reset",on_click=_update_slider)

description = st.text_input("Enter a description for the save file:")

if st.button("Submit"):
    scope = [‘https://spreadsheets.google.com/feeds’, ‘https://www.googleapis.com/auth/drive’]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets[“gcp_service_account”], scope)
    client = gspread.authorize(credentials)
    dfall = pd.DataFrame(all_data, index=[0])
    dfall[“Total Vote Count Forecast”] = GPSvote
    dfall[“Not Vote GPS”] = nonGPSvote
    dfall[“Total Voter”] = total.values
    dfall[“Simple Majority Votes”] = GPSwin
    dfall[“Two Third Winning”] = GPSwin23
    dfall[“Result”] = text_result
    dfall.insert(0, “Description Save File”, description)
    dfall.insert(1, “Parliament”, level, True)
    dfall.insert(2, “District”, d_name, True)
    dfall[“Datetime”] = datetime.datetime.now().strftime(“%Y-%m-%d %H:%M:%S”)
    sheet = client.open_by_url(st.secrets[“private_gsheets_url”])
    worksheet = sheet.get_worksheet(0)
    worksheet.append_rows(dfall.values.tolist())

