import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="MyCiTi Dashboard",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("MyCiTi Data Dashboard")

# ---------------- HELPER FUNCTIONS ----------------
@st.cache_data(ttl=300)  # Cache data for 5 minutes
def load_data():
    """Load data from database with connection handling and caching"""
    conn = None
    try:
        # Try local connection first
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Keleb@g!le3#",
                database="my_insights"
            )
        except Exception:
            # Fall back to remote connection
            conn = mysql.connector.connect(
                host="b3d9ojgfxvuk4gp7j3pn-mysql.services.clever-cloud.com",
                user="uliccdliuhdciszr",
                password="3TrDySYbfVk0PXxEsFpu",
                database="b3d9ojgfxvuk4gp7j3pn"
            )
        
        # Load data
        routes = pd.read_sql("SELECT * FROM routes", conn)
        stops = pd.read_sql("SELECT * FROM stops", conn)
        
        return routes, stops
    
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        st.stop()
    
    finally:
        if conn and conn.is_connected():
            conn.close()

def calculate_metrics(routes_df, stops_df):
    """Calculate key metrics for the dashboard"""
    total_routes = len(routes_df)
    active_stops = len(stops_df[stops_df['stop_status'] == 'Active'])
    avg_stops = active_stops / total_routes if total_routes > 0 else 0
    
    shelter_types = ['Full Shelter', 'Extended Shelter', 'Cantilever Shelter']
    sheltered_stops = len(stops_df[stops_df['stop_description'].isin(shelter_types)])
    shelter_pct = (sheltered_stops / len(stops_df)) * 100
    
    return {
        'total_routes': total_routes,
        'active_stops': active_stops,
        'avg_stops': avg_stops,
        'shelter_pct': shelter_pct
    }

# Load data
try:
    with st.spinner('Loading data...'):
        routes, stops = load_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    # Logo/app name
    st.markdown(
        """
        <div style='display:flex;align-items:center;margin-bottom:20px;'>
            <div style='font-weight:700;font-size:24px;color:#1E88E5;'>MyInsight</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.header("Filters")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now()
        )
    
    # Route filters
    route_type = st.multiselect(
        "Route Type",
        options=routes["route_type"].unique(),
        default=routes["route_type"].unique()
    )
    
    route_status = st.multiselect(
        "Route Status",
        options=routes["route_status"].unique(),
        default=routes["route_status"].unique()
    )
    
    # Filter routes based on type and status
    filtered_routes = routes[
        (routes["route_type"].isin(route_type)) & 
        (routes["route_status"].isin(route_status))
    ]
    
    selected_routes = st.multiselect(
        "Select Routes",
        options=filtered_routes["route_name"].sort_values().unique(),
        default=filtered_routes["route_name"].sort_values().unique()[:1]
    )

# Filter route details
route_details = routes[routes["route_name"].isin(selected_routes)]

# Calculate metrics
metrics = calculate_metrics(route_details, stops)

# ---------------- METRICS ----------------
st.header("📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Routes", f"{metrics['total_routes']:,}")
with col2:
    st.metric("Active Stops", f"{metrics['active_stops']:,}")
with col3:
    st.metric("Avg. Stops per Route", f"{metrics['avg_stops']:.1f}")
with col4:
    st.metric("Sheltered Stops", f"{metrics['shelter_pct']:.1f}%")

# ---------------- MAP AND ANALYSIS ----------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺 Stop Locations")
    if "latitude" in stops.columns and "longitude" in stops.columns:
        # Filter stops for selected routes if any routes are selected
        if selected_routes:
            # TODO: Add route-stop relationship filtering
            stops_for_map = stops
        else:
            stops_for_map = stops
        
        stops_for_map = stops_for_map.rename(columns={"latitude": "lat", "longitude": "lon"})
        st.map(stops_for_map)
    else:
        st.error("Stops table has no 'latitude' and 'longitude' fields — re-run ETL")

with col2:
    st.subheader("📊 Area Analysis")
    
    # Group stops by area using latitude
    lat_bins = pd.qcut(stops["latitude"], q=5, labels=[
        "North",
        "North-Central",
        "Central",
        "South-Central",
        "South"
    ])
    stops["area"] = lat_bins
    
    area_counts = stops.groupby("area").size().reset_index(name="count")
    fig = px.bar(
        area_counts,
        x="area",
        y="count",
        title="Stop Distribution by Area",
        labels={"count": "Number of Stops", "area": "Area"}
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROUTE DETAILS ----------------
st.header("🚌 Route Information")

tab1, tab2 = st.tabs(["Route Details", "Stop List"])

with tab1:
    # Show route details in a clean table
    if not route_details.empty:
        route_display = route_details.drop(columns=["geometry"], errors="ignore")
        st.dataframe(
            route_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Select one or more routes to view details")

with tab2:
    # Show stops in a searchable table
    if "latitude" in stops.columns and "longitude" in stops.columns:
        display_cols = [
            "stop_name", "stop_type", "stop_status",
            "stop_description"
        ]
        st.dataframe(
            stops[display_cols],
            use_container_width=True,
            hide_index=True
        )