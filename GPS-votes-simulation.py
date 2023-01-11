import streamlit as st
import pandas as pd
import requests
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
st.sidebar.title("Forecast Category")
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
                       replace('o90', 'Over 90 year olds ').replace('b20', 'Below 20 year olds').
                       replace('20s', '20 - 29 year olds').replace('30s', '30 - 39 year olds').
                       replace('40s', '40 - 49 year olds').replace('50s', '50 - year olds').
                       replace('60s', '60 - 69 year olds').replace('70s', '70 - 79 year olds').
                       replace('80s', '80 - 89 year olds').title() for col in age_columns}
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
            slider_values1[column_name] = st.slider("", 0, 100, 72, key=column_name, format='%d%%')
    with col3:
        st.markdown("#### GPS support forecast")
        st.markdown(f"# ")
        slider_values = {}
        for i, column_name in enumerate(renamed_columns.values()):
            key = f"slider_col2_{column_name}"
            slider_values[column_name] = st.slider("", 0, 100, 70, key=key, format='%d%%')
    with col4:
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
            GPSvote += value
    nonGPSvote = total.values - GPSvote
    GPSwin = int((total.values)[0]/2 + 1)
    GPSwin23 = int((total.values)[0]/3 + GPSwin)
    st.markdown(GPSwin23)
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
            slider_values1[column_name] = st.slider("", 0, 100, 72, key=column_name, format='%d%%')
    with col3:
        st.markdown("#### GPS support forecast")
        st.markdown(f"# ")
        slider_values = {}
        for i, column_name in enumerate(renamed_columns.values()):
            key = f"slider_col2_{column_name}"
            slider_values[column_name] = st.slider("", 0, 100, 70, key=key, format='%d%%')
    with col4:
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
            GPSvote += value
    nonGPSvote = total.values - GPSvote
    GPSwin = int((total.values)[0]/2 + 1)
    GPSwin23 = int((total.values)[0]/3 + GPSwin)
    st.markdown(GPSwin23)
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
