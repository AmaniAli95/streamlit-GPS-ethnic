import streamlit as st
import pandas as pd
import requests
from google.oauth2 import service_account
from gsheetsdb import connect
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pytz
import plotly.express as px
tz = pytz.timezone('Asia/Kuala_Lumpur')
st.set_page_config(layout="wide")

url = "https://github.com/AmaniAli95/streamlit-GPS-ethnic/raw/main/demographic.csv"
df = pd.read_csv(url)
age_columns = [col for col in df.columns if col.startswith('age_group|')]
for col in age_columns:
    df[col] = df[col].astype(str)
    df[col] = df[col].apply(lambda x: x.replace(',', ''))
    df[col] = df[col].astype(int)
st.title("GPS Votes Simulation")

#sidebar
chart_type = st.sidebar.radio('Select Category',('Ethnic', 'Age'))

# Dropdown
def filter_data(level):
    return df[df['P'] == level]
def create_level_selectbox():
    level_index = st.session_state.get("level_index", 0)
    level = st.selectbox("Select Parliament:", df['P'].dropna().unique().tolist(), index=level_index)
    st.session_state["level_index"] = df['P'].dropna().unique().tolist().index(level)
    return level
def create_dname_selectbox():
    dname_index = st.session_state.get("dname_index", 0)
    d_name = st.selectbox("Select District:", filtered_df['D'].dropna().unique().tolist(), index=dname_index)
    st.session_state["dname_index"] = filtered_df['D'].dropna().unique().tolist().index(d_name)
    return d_name

df['P'] = df.apply(lambda row: row['P_code'] + ' ' + row['P_name'], axis=1)
df['D'] = df.apply(lambda row: row['D_code'] + ' ' + row['D_name'], axis=1)
level = create_level_selectbox()
filtered_df = filter_data(level)
d_name = create_dname_selectbox()

#Gsheet db
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(credentials)
sheet = client.open_by_url(st.secrets["private_gsheets_url"])

#retrieve data
def create_recent_save_data_selectbox(worksheet, d_name):
    data = worksheet.get_all_values()
    df2 = pd.DataFrame(data[1:], columns=data[0])
    filtered_df2 = df2.loc[df2["District"] == d_name]
    selectname_options = filtered_df2["Name Save Data"].dropna().unique().tolist()
    if selectname_options:
        return st.sidebar.selectbox('Recent Save Data:', selectname_options, disabled=False)
    else:
        return st.sidebar.selectbox('Recent Save Data:',[], disabled=True)
    
if chart_type == "Ethnic":
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_values()
    df2 = pd.DataFrame(data[1:], columns=data[0])
    selected_name = create_recent_save_data_selectbox(worksheet, d_name)

elif chart_type == "Age":
    worksheet = sheet.get_worksheet(1)
    data = worksheet.get_all_values()
    df2 = pd.DataFrame(data[1:], columns=data[0])
    selected_name = create_recent_save_data_selectbox(worksheet, d_name)

#Number of Registered Voters
def to_percentage(val):
    return '{:.2f}'.format(val)

#age
if chart_type == "Age":
    st.markdown("### Number of Registered Voters")
    selected_rows = df[df['D'] == d_name]
    age_columns = [col for col in df.columns if col.startswith('age_group|')]
    renamed_columns = {col: col.replace('age_group|', '').replace('_', ' ').
                       replace('o90', 'Over 90 y/o').replace('b20', 'Below 20 y/o').
                       replace('20s', '20 - 29 y/o').replace('30s', '30 - 39 y/o').
                       replace('40s', '40 - 49 y/o').replace('50s', '50 - 50 y/o').
                       replace('60s', '60 - 69 y/o').replace('70s', '70 - 79 y/o').
                       replace('80s', '80 - 89 y/o') for col in age_columns}
    selected_rows.rename(columns=renamed_columns, inplace=True)
    selected_rows[list(renamed_columns.values())] = selected_rows[list(renamed_columns.values())].apply(pd.to_numeric, errors='coerce')
    selected_rows[list(renamed_columns.values())].fillna(0, inplace=True)
    total = selected_rows[list(renamed_columns.values())].astype(int).sum(axis=1)
    total_df = pd.DataFrame({'Total': total})
    dfnew = (pd.concat([selected_rows[list(renamed_columns.values())], total_df], axis=1))
    percentages = dfnew[list(renamed_columns.values())].div(total, axis=0).mul(100)
    dfnew = dfnew.append(percentages.applymap(to_percentage), ignore_index=True)
    #dfnew = dfnew.append(percentages, ignore_index=True)
    dfnew.insert(0, 'Age Group', ['Voters','Percentage (%)'])
    dfnew.at[1, dfnew.columns[10]] = 100
    dfnew['Total'] = dfnew['Total'].astype(int)
    html = (
        dfnew
        .style.set_properties(**{'text-align': 'center'})
        .hide_index()
        .render()
    )
    st.write(html, unsafe_allow_html=True)
    
    ##barchart
    x = dfnew.iloc[0, :].values
    y = dfnew.iloc[1, :].values
    fig = px.bar(dfnew, x=x, y=y, color=y, height=400)
    fig.add_scatter(x=x, y=y, mode='lines', name='Curve')

    st.plotly_chart(fig)
    
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
            all_data[f"{column_name} | Pct GPS Support Forecast"] = slider_values[column_name]
            all_data[f"{column_name} | Vote Count Forecast"] = value
            GPSvote += value
    nonGPSvote = total.values - GPSvote
    GPSwin = int((total.values)[0]/2 + 1)
    GPSwin23 = int((total.values)[0]/3 + GPSwin)
    remGPSvote = abs(GPSvote - GPSwin)
    st.markdown(f"#### In order for GPS to earn a simple majority, it needs {GPSwin} support while to earn 2/3 votes, it needs {GPSwin23} support")
    st.markdown(f"#### Currently, it expected to garner {GPSvote} support")
    if GPSvote >= GPSwin23:
        result = "<h2 style='color: green; animation: pulse 3s infinite'>GPS is Winning. It forecast to win 2/3 votes</h2>"
    elif GPSvote > nonGPSvote:
        result = "<h2 style='color: green; animation: pulse 3s infinite'>GPS is Winning</h2>"
    else:
        result = "<h2 style='color: red; animation: pulse 3s infinite'>GPS is Losing - it needs {} support to win</h2>".format(remGPSvote)
    st.markdown(result, unsafe_allow_html=True)
    soup = BeautifulSoup(result, 'html.parser')
    text_result = soup.h2.text
    
#ethnic
elif chart_type == "Ethnic":
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
    dfnew.insert(0, 'Ethnic', ['Voters','Percentage (%)'])
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
            all_data[f"{column_name} | Pct GPS Support Forecast"] = slider_values[column_name]
            all_data[f"{column_name} | Vote Count Forecast"] = value
            GPSvote += value
    nonGPSvote = total.values - GPSvote
    GPSwin = int((total.values)[0]/2 + 1)
    GPSwin23 = int((total.values)[0]/3 + GPSwin)
    remGPSvote = abs(GPSvote - GPSwin)
    st.markdown(f"#### In order for GPS to earn a simple majority, it needs {GPSwin} support while to earn 2/3 votes, it needs {GPSwin23} support")
    st.markdown(f"#### Currently, it expected to garner {GPSvote} support")
    if GPSvote >= GPSwin23:
        result = "<h2 style='color: green; animation: pulse 3s infinite'>GPS is Winning. It forecast to win 2/3 votes</h2>"
    elif GPSvote > nonGPSvote:
        result = "<h2 style='color: green; animation: pulse 3s infinite'>GPS is Winning</h2>"
    else:
        result = "<h2 style='color: red; animation: pulse 3s infinite'>GPS is Losing - it needs {} support to win</h2>".format(remGPSvote)
    st.markdown(result, unsafe_allow_html=True)
    soup = BeautifulSoup(result, 'html.parser')
    text_result = soup.h2.text  

#reset btn
updateBtn_disabled = True
def _reset_slider():
    global updateBtn_disabled
    updateBtn_disabled = True
    for i, column_name in enumerate(renamed_columns.values()):
        if column_name not in st.session_state:
           st.session_state[column_name] = 72
        st.session_state[column_name] = 72
    for i, column_name in enumerate(renamed_columns.values()):
        key = f"slider_col3_{column_name}"
        if key not in st.session_state:
           st.session_state[key] = 70
        st.session_state[key] = 70  
    st.session_state["name"] = f"{d_name}-{datetime.datetime.now(tz).strftime('%Y%m%d')}-{datetime.datetime.now(tz).strftime('%H%M')}"
    st.session_state["desc"] = " "

def _load_slider():
    global updateBtn_disabled
    updateBtn_disabled = False
    selected_row = df2.loc[df2["Name Save Data"] == selected_name]
    st.session_state["level_index"] = df['P'].dropna().unique().tolist().index(selected_row["Parliament"].values[0])
    filtered_df = filter_data(selected_row["Parliament"].values[0])
    st.session_state["dname_index"] = filtered_df['D'].dropna().unique().tolist().index(selected_row["District"].values[0])
    for i, column_name in enumerate(renamed_columns.values()):
        st.session_state[column_name] = int(selected_row[f"{column_name} | Pct Turnout Forecast"].values[0])
    for i, column_name in enumerate(renamed_columns.values()):
        key = f"slider_col3_{column_name}"
        st.session_state[key] = int(selected_row[f"{column_name} | Pct GPS Support Forecast"].values[0])
    st.session_state["name"] = selected_row["Name Save Data"].values[0]
    st.session_state["desc"] =  selected_row["Description Save Data"].values[0]
    return st.session_state["name"], st.session_state["desc"]
loadBtn = st.sidebar.button("Load",on_click=_load_slider)  

updateBtn_disabled = True
#check loadBtn
if not loadBtn and "name" not in st.session_state:
    st.session_state["name"] = f"{d_name}-{datetime.datetime.now(tz).strftime('%Y%m%d')}-{datetime.datetime.now(tz).strftime('%H%M')}"
    st.session_state["desc"] =  " "
    name = st.text_input("Enter a name for save data:",value = st.session_state["name"])
    description = st.text_input("Enter a description for save data:", value = st.session_state["desc"])
    updateBtn = st.button("Update", disabled=updateBtn_disabled)
elif loadBtn and "name" in st.session_state:
    updateBtn_disabled = False
    name = st.text_input("Enter a name for save data:",value = st.session_state["name"])
    description = st.text_input("Enter a description for save data:", value = st.session_state["desc"])
    updateBtn = st.button("Update", disabled=updateBtn_disabled)
elif not loadBtn and st.session_state["name"] != f"{d_name}-{datetime.datetime.now(tz).strftime('%Y%m%d')}-{datetime.datetime.now(tz).strftime('%H%M')}":
    updateBtn_disabled = False
    name = st.text_input("Enter a name for save data:",value = st.session_state["name"])
    description = st.text_input("Enter a description for save data:", value = st.session_state["desc"])
    updateBtn = st.button("Update", disabled=updateBtn_disabled)
else:
    name = st.text_input("Enter a name for save data:",value = st.session_state["name"])
    description = st.text_input("Enter a description for save data:", value = st.session_state["desc"])
    updateBtn = st.button("Update", disabled=updateBtn_disabled)
    
#updateBtn
if updateBtn:
    dfall = pd.DataFrame(all_data, index=[0])
    dfall["Total Vote Count Forecast"] = GPSvote
    dfall["Not Vote GPS"] = nonGPSvote
    dfall["Total Voter"] = total.values
    dfall["Simple Majority Votes"] = GPSwin
    dfall["Two Third Winning"] = GPSwin23
    dfall["Result"] = text_result
    dfall.insert(0, "Name Save Data", name)
    dfall.insert(1, "Description Save Data", description)
    dfall.insert(2, "Parliament", level, True)
    dfall.insert(3, "District", d_name, True)
    dfall["Datetime"] = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    if chart_type == "Ethnic":
        worksheet = sheet.get_worksheet(0)
        name_data = dfall["Name Save Data"].values[0]
        results = worksheet.find(name_data)
        if results:
            row_number = results.row
            row_data = worksheet.row_values(row_number)
            for i in range(len(dfall.columns)):
                worksheet.update_cell(row_number, i+1, str(dfall.iloc[0,i]))
    else:
        worksheet = sheet.get_worksheet(1)
        data = worksheet.get_all_values()
        name_data = dfall["Name Save Data"].values[0]
        results = worksheet.find(name_data)
        if results:
            row_number = results.row
            row_data = worksheet.row_values(row_number)
            for i in range(len(dfall.columns)):
                worksheet.update_cell(row_number, i+1, str(dfall.iloc[0,i]))
                    
#resetBtn = st.button("Reset",on_click=_reset_slider)
resetBtn = st.button("Reset",on_click=lambda: _reset_slider())

#submitBtn
# Check if save data name already exists in the Google Sheet
if chart_type == "Ethnic":
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_values()
    df2 = pd.DataFrame(data[1:], columns=data[0])
    existing_names = df2["Name Save Data"].tolist()
else:
    worksheet = sheet.get_worksheet(1)
    data = worksheet.get_all_values()
    df2 = pd.DataFrame(data[1:], columns=data[0])
    existing_names = df2["Name Save Data"].tolist()
if name in existing_names:
    st.warning("Name already exists. Please enter a new name for save data.")
else:
    if st.button("Submit"):
        dfall = pd.DataFrame(all_data, index=[0])
        dfall["Total Vote Count Forecast"] = GPSvote
        dfall["Not Vote GPS"] = nonGPSvote
        dfall["Total Voter"] = total.values
        dfall["Simple Majority Votes"] = GPSwin
        dfall["Two Third Winning"] = GPSwin23
        dfall["Result"] = text_result
        dfall.insert(0, "Name Save Data", name)
        dfall.insert(1, "Description Save Data", description)
        dfall.insert(2, "Parliament", level, True)
        dfall.insert(3, "District", d_name, True)
        dfall["Datetime"] = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_rows(dfall.values.tolist())
