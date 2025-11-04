from extract import get_data
from transform import transform_routes, transform_stops
from load import load_csv

def main():
    # Extract
    routes_data, stops_data = get_data()

    # Transform
    df_routes = transform_routes(routes_data)
    df_stops = transform_stops(stops_data)

    # Load
    load_csv(df_routes, "routes.csv")
    load_csv(df_stops, "stops.csv")

if __name__ == "__main__":
    main()
