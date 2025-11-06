# etl/load_to_mysql.py

import pandas as pd
import mysql.connector
from mysql.connector import Error

# MySQL connection config
DB_CONFIG = {
    'host': 'b3d9ojgfxvuk4gp7j3pn-mysql.services.clever-cloud.com',       # or your MySQL server host
    'user': 'uliccdliuhdciszr',
    'password': '3TrDySYbfVk0PXxEsFpu',
    'database': 'b3d9ojgfxvuk4gp7j3pn'
}

# File paths (adjust if running from project root)
ROUTES_CSV = "../data/processed/routes.csv"
STOPS_CSV = "../data/processed/stops.csv"

def load_csv_to_mysql(csv_file, table_name, unique_column):
    """Load CSV data into MySQL table, skipping duplicates."""
    df = pd.read_csv(csv_file)

    # Drop duplicate rows based on the unique column
    before = len(df)
    df = df.drop_duplicates(subset=[unique_column])
    after = len(df)
    print(f"Dropped {before - after} duplicate rows in {table_name} based on {unique_column}")

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Build the column and placeholders string
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))

        # Convert DataFrame to list of tuples for executemany
        values = [tuple(x) for x in df.to_numpy()]

        sql = f"INSERT IGNORE INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.executemany(sql, values)
        conn.commit()

        print(f"Inserted {cursor.rowcount} rows into {table_name}")

    except Error as e:
        print("Error while connecting or inserting into MySQL:", e)

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print(f"Connection to MySQL closed for table {table_name}")

if __name__ == "__main__":
    load_csv_to_mysql(ROUTES_CSV, 'routes', 'route_id')
    load_csv_to_mysql(STOPS_CSV, 'stops', 'stop_id')
