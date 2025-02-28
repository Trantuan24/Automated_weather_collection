import os
import json
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
from fetch_weather import get_weather_dataframe
from transform_data import clean_and_transform
from data_quality_check import validate_data

# Read DB configuration from JSON file
CONFIG_PATH = "config/db_config.json"
with open(CONFIG_PATH, "r") as config_file:
    DB_CONFIG = json.load(config_file)

def connect_db():
    """Connect to PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ PostgreSQL connection error: {e}")
        return None

def create_table_if_not_exists(conn, table_name):
    """Create table if it does not exist, with fixed schema."""
    # Define common schema for both tables (you can adjust if needed)
    create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            city_id INTEGER,
            city_name TEXT,
            country TEXT,
            collected_at TIMESTAMP,
            temperature FLOAT,
            feels_like FLOAT,
            humidity INTEGER,
            pressure INTEGER,
            wind_speed FLOAT,
            wind_direction INTEGER,
            cloud_cover INTEGER,
            weather TEXT,
            visibility INTEGER,
            dew_point FLOAT,
            precipitation FLOAT,
            PRIMARY KEY (city_id, collected_at)
        );
    """
    with conn.cursor() as cur:
        cur.execute(create_sql)
        conn.commit()

def load_to_postgres(df, table_name):
    """Load data into PostgreSQL."""
    conn = connect_db()
    if not conn:
        return
    
    # Before inserting, create the table if it does not exist
    create_table_if_not_exists(conn, table_name)
    
    try:
        with conn.cursor() as cur:
            cols = ", ".join(df.columns)
            values = [tuple(row) for row in df.to_numpy()]
            insert_query = f"""
                INSERT INTO {table_name} ({cols})
                VALUES %s
                ON CONFLICT (city_id, collected_at) DO NOTHING
            """
            execute_values(cur, insert_query, values)
            conn.commit()
            print(f"✅ Inserted {len(df)} rows into {table_name}")
    except Exception as e:
        print(f"❌ Error inserting data into {table_name}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    raw_df = get_weather_dataframe()
    clean_df = clean_and_transform(raw_df)
    df_pass, df_fail = validate_data(clean_df)
    
    # Save valid data into weather_data table
    load_to_postgres(df_pass, "weather_data")
    # Save invalid data into invalid_weather_data table
    load_to_postgres(df_fail, "invalid_weather_data")
