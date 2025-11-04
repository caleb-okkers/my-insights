# import json

# def get_data():
#     """Extract raw GeoJSON data and return as Python dicts."""
#     routes_file = "../data/raw/Integrated_rapid_transit_(IRT)_system_MyCiTi_Bus_Routes.geojson"
#     stops_file = "../data/raw/Integrated_rapid_transit_(IRT)_system_MyCiTi_Bus_Stops.geojson"

#     with open(routes_file) as f:
#         routes_data = json.load(f)

#     with open(stops_file) as f:
#         stops_data = json.load(f)

#     return routes_data, stops_data

# import pandas as pd
# import json
# from pathlib import Path

# RAW_DIR = Path("../data/raw")

# def get_data():
#     # Stop files
#     stops_file = RAW_DIR / "Integrated_rapid_transit_(IRT)_system_MyCiTi_Bus_Stops.geojson"
#     routes_file = RAW_DIR / "Integrated_rapid_transit_(IRT)_system_MyCiTi_Bus_Routes.geojson"

#     # Read GeoJSON as dict
#     with open(stops_file) as f:
#         stops_json = json.load(f)
#     with open(routes_file) as f:
#         routes_json = json.load(f)

#     # Convert features to DataFrame
#     df_stops = pd.json_normalize(stops_json['features'])
#     df_routes = pd.json_normalize(routes_json['features'])

#     return df_routes, df_stops

import pandas as pd
import json
from pathlib import Path

RAW_DIR = Path("../data/raw")

def get_data():
    stops_file = RAW_DIR / "Integrated_rapid_transit_(IRT)_system_MyCiTi_Bus_Stops.geojson"
    routes_file = RAW_DIR / "Integrated_rapid_transit_(IRT)_system_MyCiTi_Bus_Routes.geojson"

    # Load JSON
    with open(stops_file) as f:
        stops_json = json.load(f)
    with open(routes_file) as f:
        routes_json = json.load(f)

    # Convert 'features' to DataFrame
    df_stops = pd.json_normalize(stops_json['features'])
    df_routes = pd.json_normalize(routes_json['features'])

    return df_routes, df_stops
