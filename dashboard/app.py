import streamlit as st
import pandas as pd
import mysql.connector
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
        background-color: #5C5B5B;
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

def calculate_metrics(routes_df, stops_df, all_routes_df=None):
    """Calculate key metrics for the dashboard"""
    total_routes = len(all_routes_df) if all_routes_df is not None else len(routes_df)
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
            <div style='font-weight:700;font-size:24px;color:#1E88E5;'>MyInsights</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize session states
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    if 'selected_routes' not in st.session_state:
        st.session_state.selected_routes = []

    # Navigation
    st.header("Navigation")
    st.session_state.page = st.radio("Select Page", ["Home", "Routes", "Stops"])
    

    
    # Get active routes
    active_routes = routes[routes["route_status"] == "Active"]
    
    # Route selection
    st.session_state.selected_routes = st.multiselect(
        "Select Routes",
        options=active_routes["route_name"].sort_values().unique(),
        default=[]
    )

# Get filtered routes based on selection
route_details = routes[routes["route_name"].isin(st.session_state.selected_routes)] if st.session_state.selected_routes else routes

# Calculate metrics
metrics = calculate_metrics(route_details, stops, routes)

# ---------------- MAIN CONTENT ----------------
if st.session_state.page == "Home":
    # ---------------- METRICS ----------------
    st.header("📊 Key Performance Indicators")
    metrics = calculate_metrics(route_details, stops, routes)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Routes", f"{metrics['total_routes']:,}")
    with col2:
        st.metric("Active Stops", f"{metrics['active_stops']:,}")
    with col3:
        st.metric("Avg. Stops per Route", f"{metrics['avg_stops']:.1f}")
    with col4:
        st.metric("Sheltered Stops", f"{metrics['shelter_pct']:.1f}%")

    # ---------------- MAP ----------------
    st.subheader("🗺 Stop Locations")
    if "latitude" in stops.columns and "longitude" in stops.columns:
        stops_for_map = stops.rename(columns={"latitude": "lat", "longitude": "lon"})
        st.map(stops_for_map)
    else:
        st.error("Stops table has no 'latitude' and 'longitude' fields — re-run ETL")

    # ---------------- ROUTES TABLE ----------------
    st.subheader("🚌 All Routes")
    route_display = routes.drop(columns=["geometry"], errors="ignore")
    st.dataframe(
        route_display,
        use_container_width=True,
        hide_index=True
    )

elif st.session_state.page == "Routes":
    st.header("🚌 Route Analysis")
    
    if st.session_state.selected_routes:
        # Show selected route details
        st.subheader("Selected Route Details")
        route_display = route_details.drop(columns=["geometry"], errors="ignore")
        st.dataframe(
            route_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Please select one or more routes from the sidebar to view details")

elif st.session_state.page == "Stops":
    st.header("🚏 Stop Analysis")
    
    # Area Distribution
    st.subheader("📊 Stop Distribution by Area")
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
    fig.update_layout(
        showlegend=False,
        yaxis=dict(
            range=[0, 200],  # Set y-axis range from 0 to 200
            dtick=50  # Set tick marks every 50 units
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Stop Types Distribution
    st.subheader("📊 Stop Types Distribution")
    type_counts = stops.groupby("stop_type").size().reset_index(name="count")
    fig = px.pie(
        type_counts,
        names="stop_type",
        values="count",
        title="Distribution of Stop Types"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Stop List
    st.subheader("🚏 Stop List")
    display_cols = [
        "stop_name", "stop_type", "stop_status",
        "stop_description"
    ]
    st.dataframe(
        stops[display_cols],
        use_container_width=True,
        hide_index=True
    )