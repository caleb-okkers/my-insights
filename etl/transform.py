# import pandas as pd

# # Transform Routes
# def transform_routes(df):
#     df_clean = df.rename(columns={
#         "properties.RT_NAME": "route_name",
#         "properties.RT_NMBR": "route_number",
#         "properties.RT_TYPE": "route_type",
#         "properties.RT_STS": "route_status",
#         "geometry.coordinates": "geometry"
#     })

#     df_clean = df_clean[["route_number", "route_name", "route_type", "route_status", "geometry"]]

#     # Add route_id column
#     df_clean["route_id"] = df_clean.index + 1

#     # Reorder columns
#     df_clean = df_clean[["route_id", "route_number", "route_name", "route_type", "route_status", "geometry"]]

#     return df_clean


# # Transform Stops
# def transform_stops(df):
#     df_clean = df.rename(columns={
#         "properties.OBJECTID": "stop_id",
#         "properties.STOP_NAME": "stop_name",
#         "properties.STOP_TYPE": "stop_type",
#         "properties.STOP_STS": "stop_status",
#         "properties.STOP_DSCR": "stop_description",
#         "geometry.coordinates": "coordinates"
#     })

#     # Extract lat/lon
#     df_clean["longitude"] = df_clean["coordinates"].apply(lambda x: x[0])
#     df_clean["latitude"] = df_clean["coordinates"].apply(lambda x: x[1])

#     # Keep relevant columns
#     df_clean = df_clean[["stop_id", "stop_name", "stop_type", "stop_status", "stop_description", "longitude", "latitude"]]

#     return df_clean

import pandas as pd

# Transform Routes
def transform_routes(df):
    df_clean = df.rename(columns={
        "properties.RT_NAME": "route_name",
        "properties.RT_NMBR": "route_number",
        "properties.RT_TYPE": "route_type",
        "properties.RT_STS": "route_status",
        "geometry.coordinates": "geometry"
    })

    # Keep only relevant columns
    df_clean = df_clean[["route_number", "route_name", "route_type", "route_status", "geometry"]]

    # Deduplicate based on route_number + route_name
    before = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=["route_number", "route_name"])
    print(f"Dropped {before - len(df_clean)} duplicate routes")

    # Reassign route_id sequentially
    df_clean["route_id"] = range(1, len(df_clean) + 1)

    # Reorder columns
    df_clean = df_clean[["route_id", "route_number", "route_name", "route_type", "route_status", "geometry"]]

    return df_clean


# Transform Stops
def transform_stops(df):
    df_clean = df.rename(columns={
        "properties.OBJECTID": "stop_id",
        "properties.STOP_NAME": "stop_name",
        "properties.STOP_TYPE": "stop_type",
        "properties.STOP_STS": "stop_status",
        "properties.STOP_DSCR": "stop_description",
        "geometry.coordinates": "coordinates"
    })

    # Extract lat/lon
    df_clean["longitude"] = df_clean["coordinates"].apply(lambda x: x[0])
    df_clean["latitude"] = df_clean["coordinates"].apply(lambda x: x[1])

    # Keep relevant columns
    df_clean = df_clean[["stop_name", "stop_type", "stop_status", "stop_description", "longitude", "latitude"]]

    # Deduplicate based on stop_name + coordinates
    before = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=["stop_name", "longitude", "latitude"])
    print(f"Dropped {before - len(df_clean)} duplicate stops")

    # Reassign stop_id sequentially
    df_clean["stop_id"] = range(1, len(df_clean) + 1)

    # Reorder columns
    df_clean = df_clean[["stop_id", "stop_name", "stop_type", "stop_status", "stop_description", "longitude", "latitude"]]

    return df_clean
