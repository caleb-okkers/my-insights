import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="MyCiTi Dashboard", layout="wide")

st.title("MyCiTi Data Dashboard")

# ---------------- DB CONNECTION ----------------
try:
    conn = mysql.connector.connect(
        host="b3d9ojgfxvuk4gp7j3pn-mysql.services.clever-cloud.com",
        user="uliccdliuhdciszr",
        password="3TrDySYbfVk0PXxEsFpu",
        database="b3d9ojgfxvuk4gp7j3pn"
    )

    routes = pd.read_sql("SELECT * FROM routes", conn)
    stops = pd.read_sql("SELECT * FROM stops", conn)

    conn.close()
except:
    st.error("Could not connect to database. Make sure MySQL is running.")
    st.stop()

# ---------------- SIDEBAR FILTER ----------------
# Small logo / app name in the sidebar (top-left corner)
st.sidebar.markdown(
        """
        <div style='display:flex;align-items:center;'>
            <div style='font-weight:700;font-size:20px;'>MyInsight</div>
        </div>
        """,
        unsafe_allow_html=True,
)

st.sidebar.header("Filters")
selected_route = st.sidebar.selectbox(
    "Choose a route",
    options=routes["route_name"].sort_values().unique()
)

# Filter routes
route_details = routes[routes["route_name"] == selected_route]

# Remove geometry column (if present) before displaying selected route details
route_details_display = route_details.drop(columns=["geometry"], errors="ignore")
st.subheader(f"Route Selected: **{selected_route}**")
st.dataframe(route_details_display)

# ---------------- MAP OF STOPS ----------------
st.subheader("🗺 Stop Locations")

if "latitude" in stops.columns and "longitude" in stops.columns:
    stops_for_map = stops.rename(columns={"latitude": "lat", "longitude": "lon"})
    st.map(stops_for_map)
else:
    st.error("Stops table has no 'latitude' and 'longitude' fields — re-run ETL")

# ---------------- STOPS TABLE ----------------
st.subheader("All Stops")
# Hide latitude and longitude columns for the All Stops table view
st.dataframe(stops.drop(columns=["latitude", "longitude"], errors="ignore"))
