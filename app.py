# app.py

import streamlit as st
import pandas as pd
import requests
import altair as alt
import time
from datetime import datetime

def process_AllStates():
    df = get_DF()
    if df.empty:
        st.warning("No flights found for the selected filters.")
        st.stop()

    if "on_ground" in df.columns:
        if ground == "Only On Ground":
            df = df[df["on_ground"] == True]
        elif ground == "Only In Air":
            df = df[df["on_ground"] == False]
    else:
        st.warning("'on_ground' column not found.")
        
    st.dataframe(df, use_container_width=True)
    st.write(f"### Total flights found: {len(df)}")
    
def filter_data(sWord, sData):
        df = get_DF()  
        filtered_df = df[df[sData].str.lower() == sWord.lower()]
        
        if sData:
            if "on_ground" in filtered_df.columns:
                if ground == "Only On Ground":
                    filtered_df = filtered_df[filtered_df["on_ground"] == True]
                elif ground == "Only In Air":
                    filtered_df = filtered_df[filtered_df["on_ground"] == False]
            else:
                st.warning("'on_ground' column not found.")
            
            if filtered_df.empty:
                st.warning(f"No flights found for ICAO code '{sWord}'.")
            else:
                st.write(f"Showing flights for ICAO code: {sWord.upper()}")
                st.dataframe(filtered_df)
                st.write(f"### Total flights found: {len(filtered_df)}")

def get_DF():
    if resp.status_code != 200:
        st.error(f"Error fetching data: {resp.status_code} - {resp.reason}")
        st.stop()

    try:
        data = resp.json()
        states = data.get("states", [])
        
        columns = [
                "icao24", "callsign", "origin_country", "time_position", "last_contact",
                "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
                "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
                "spi", "position_source"
            ]

        if states:
            df = pd.DataFrame(states, columns=columns)
            return df
        else:
            st.warning("No flight state data returned.")
            st.stop()
        
    except Exception as e:
        st.error("Failed to parse response. Maybe no data or wrong credentials.")
        st.stop()
    
def goto_chk_other(resp):
    if(airport != "" and country == ""):
        with st.spinner("🔄 Connecting to OpenSky API and processing data..."):
            if resp.status_code != 200:
                st.error(f"Error fetching data: {resp.status_code} - {resp.reason}")
                st.stop()

            filter_data(airport, "icao24")  # Your data processing function
        
    elif(airport == "" and country != ""):
        with st.spinner("🔄 Connecting to OpenSky API and processing data..."):
            if resp.status_code != 200:
                st.error(f"Error fetching data: {resp.status_code} - {resp.reason}")
                st.stop()

            filter_data(country, "origin_country")  # Your data processing function

    elif(airport == "" and country != "" and ground != ""):
        with st.spinner("🔄 Connecting to OpenSky API and processing data..."):
            if resp.status_code != 200:
                st.error(f"Error fetching data: {resp.status_code} - {resp.reason}")
                st.stop()

            filter_data(ground, "on_ground")  # Your data processing function

# -------------------------------------------------------------
#             E N T R Y - P O I N T                           |
# -------------------------------------------------------------    
st.sidebar.header("🔍 Filter Flights")
airport = st.sidebar.text_input("Search by ICAO Code", "")  
country = st.sidebar.text_input("Search by Country", "")  
ground = st.sidebar.selectbox(
    "Filter by ground status",
    options=["All", "Only On Ground", "Only In Air"]
)

st.subheader("🛫 Flight State Data")

url = "https://opensky-network.org/api/states/all"
placeholder = st.empty()  # Create container for messages
placeholder.info("Fetching flights departing...")  # Show initial info
resp = requests.get(url)

if (airport == "" and country == ""):
        with st.spinner("🔄 Connecting to OpenSky API and processing data..."):
            if resp.status_code != 200:
                st.error(f"Error fetching data: {resp.status_code} - {resp.reason}")
                st.stop()
            process_AllStates()  # Your data processing function
            
if st.sidebar.button("Analyze"):
    goto_chk_other(resp)
    
placeholder.empty()  # Clear info message
placeholder.success("✅ Analysis complete.")  # Show success message
time.sleep(2)  # Keep success visible for 3 seconds
placeholder.empty()  # Clear success message
st.stop()
