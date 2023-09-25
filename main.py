import streamlit as st
import plotly.express as px
import pandas as pd
import os
import toml
import warnings
warnings.filterwarnings('ignore')
import json
import numpy as np
import pandas as pd
import pandas as pd

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Sample SuperStore USA Departement")
st.info("Click on the dates below to change the start date and the end date prefered!")


col1, col2 = st.columns((2))

# with col1:
#     st.image("img/SStore.gif")
# with col2:
#     st.image("img/SStoree.gif")


st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

df = pd.read_csv("Superstore.csv", encoding = "ISO-8859-1")


df["Order Date"] = pd.to_datetime(df["Order Date"])



# Logo Of the Web App 

st.sidebar.image("./components/image/logo.png", width=280)


# Linked CSS File 

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Config.toml For Styling 

@st.cache_data
def load_config():
    with open("config.toml") as f:
        config = toml.loads(f.read())
    return config

config = load_config()


# Getting the min and max date 
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
# Create for Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create for State
state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Create for City
city = st.sidebar.multiselect("Pick the City",df3["City"].unique())

# Filter the data based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
        
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)




us_states = json.load(open("us_states.json"))

    # Read the CSV data
df = pd.read_csv("Superstore.csv")

    # Create a mapping of state names to IDs
state_id_map = {}
for feature in us_states['features']:
        feature['id'] = feature['properties']['STATE']
        state_id_map[feature['properties']['NAME']] = feature['id']

# Function to remove commas and convert to int
def remove_commas_and_convert_to_int(s):
        if isinstance(s, str):
            return int(s.replace(",", ""))
        elif isinstance(s, (int, float)):
            return int(s)
        else:
            return s

# Apply the function to the 'Sales' column
df['Sales'] = df['Sales'].apply(remove_commas_and_convert_to_int)

# Add an 'id' column to the DataFrame
df['id'] = df['State'].apply(lambda x: state_id_map.get(x, -1))  # Use -1 as default if state not found
df['SalesScale'] = np.log10(df['Sales'])
# Streamlit app
st.subheader("Choropleth map of Superstore Sales by states")

# Create and display the choropleth map
# fig = go.Figure(go.Choropleth(
#     geojson=us_states,
#     locations=df['id'],
#     z=df['Sales'],
#     color='SalesScale',
#     autocolorscale=False,
#     marker_line_color='white',
#     colorbar_title="Sales"
# ))

color_scale = [
        [0.8, 'rgb(0,191,255)'],  
        [0.9, 'rgb(139,0,139)'],   
        [1.0, 'rgb(178,34,34)'],    
]

fig = px.choropleth(df, locations='id', geojson=us_states, color='SalesScale' , color_continuous_scale=color_scale, hover_name='State', hover_data=['Sales'])

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)'))
fig.update_layout(width=800)
st.plotly_chart(fig)


# ,scope='north america'


import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)



st.subheader('Profit by Cities (Overall profit between 2014 and 2018)')

# Read the CSV file
df = pd.read_csv("Superstore.csv")

# Create a Streamlit dropdown to select the state
selected_state = st.selectbox("Select a State", df['State'].unique())

# Filter the data for the selected state
filtered_df = df[df['State'] == selected_state]

# Aggregate profit values for cities with multiple entries
filtered_df = filtered_df.groupby('City')['Profit'].sum().reset_index()

# Create a bar chart
fig = px.bar(filtered_df, x='City', y='Profit', title=f'Profit by City in {selected_state}')
fig.update_xaxes(title_text='City')
fig.update_yaxes(title_text='Profit')

# Set the chart width to 100% of the page
fig.update_layout(width=800)  # You can adjust the width as needed

# Show the bar chart
st.plotly_chart(fig)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))


# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")










