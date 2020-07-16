#import statements
import pandas as pd
import altair as alt
import streamlit as st
import pydeck as pdk
import numpy as np
# import os 
# import psicopg2

# DATABASE_URL = os.environ['DATABASE_URL']

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')

@st.cache
# Function to load in data
def get_data():
    satelite_data = "monthly_count.csv"
    df = pd.read_csv(satelite_data)
    return df.set_index("months")

# Loading in data
try:
    df = get_data()
except:
    st.error(
        """
        **could not load data**

        Save data to same directory
    """)
data = df.T
# Title 
'''
# **Bushfires in NSW**
'''

st.image('NSW_2013.jpg', 
use_column_width=True)
'''
Image from 21/10/2013, Source [here](https://visibleearth.nasa.gov/images/82211/fires-in-new-south-wales-australia/82212w).


How intense are the bushfires in Australia? How do they progress?
Are we able to get a notion of what is going on?

Well, Australia is a big place, so in this project we will be looking at NSW only.

Let's check the number of events that happen over the years.

'''

# Selecting the specific year on a multiselect object
year = st.multiselect(
    "Choose years to see on graph", list(df.columns), ['2001', '2002']
)
if not year:
    st.error("Please select at least one year.")

# Filtering selected years
data = df.T.loc[year]
# Preparing a chckbox to look at data 
if st.checkbox('Show raw data'):
    st.subheader('number of events per month/year')
    st.write(data)


# preparing data for chart
data = pd.melt(data.T.reset_index(), id_vars=["months"]).rename(
    columns={"index": "month", "value": "Fires per month",'variable':'years'})

# Preparing chart
chart = (
    alt.Chart(data)
    .mark_area(opacity=0.3)
    .encode(
        x="months:O",
        y=alt.Y("Fires per month:Q", stack=None),
        color="years:N",
        # order="order:O"
    )
)
# plotting chart using altair(for mrore info: https://altair-viz.github.io/user_guide/encoding.html)
st.altair_chart(chart, use_container_width=True)

# Map starts beow -----------------------------

'''
### Let's take a look at the fires on a map.

The best way to look at this data is on a map. This way we can clearly understand 
the progression over time and the magnitude of the problem.

The markings below show the density of hotspots in a 1km area. 
This means that the more events that happen in the same area the stronger the color 
and the higher the bars.

We can see the information day-by-day over 2019. 
This is a great format to see how the fire fronts progressed on the most fire intense days
 of 2019.

'''

# preparing variables
DATE_TIME = "datetime"
DATA_URL = ('satelite_2019.csv')

@st.cache(persist=True)
# preparing data loadin function
def load_data():
    data = pd.read_csv(DATA_URL)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
    return data

# loading data in
df = load_data()
data = df
# month slider
month = st.slider(" Select a month to look at", 1, 12)
# Day slider
day = st.slider("Select a day to look at", 1, 31)
# map agle view
angle = st.slider("Select map angle", 1, 51,step=5)
# Filtering useing sliders
data = data[(data[DATE_TIME].dt.day == day) & (data[DATE_TIME].dt.month == month)]
# creating subheader to show what is being displayed on the map
st.subheader("Geo data on %i/%i/2019 " %(day, month))
# Getting the midpoint to zoom the map in
midpoint = (np.average(df["latitude"]), np.average(df["longitude"]))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 5, 
        "pitch": angle, 
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data,
            get_position=["longitude", "latitude"],
            radius=1000, 
            elevation_scale=6, 
            elevation_range=[0, 3000], 
            pickable=True,
            extruded=True,
        )
    ]
))
if st.checkbox('Want to know more about what we are looking at?'):
    
    st.write(
        '''The data that this project uses was collected by Nasa using the MODIS instrument. 
More information [here](https://modis.gsfc.nasa.gov/data/).

MODIS has several products, this project focuses on the active fire product. 
This product reads the brightness emitted from earth to space to determine active events.

The map represents the density of fires in NSW. The highest represent a maximum of 6 fires in a
2km radius and the lowest represent one.

want to know more about this [project?](https://juliocent.github.io/portfolio/)

''')

# if st.checkbox('Want to know more about this project'):
    
#     st.write(
#         '''under construction''')
