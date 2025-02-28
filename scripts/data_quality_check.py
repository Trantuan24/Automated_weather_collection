import pandas as pd
from datetime import datetime, timedelta

def validate_data(df):
    """
    Check data quality before loading into PostgreSQL.
    Separate valid data (df_pass) and invalid data (df_fail).
    """
    # Create a copy of the data
    df_pass = df.copy()
    df_fail = pd.DataFrame(columns=df.columns)  # Invalid data

    # 1. Check required columns for null values
    required_columns = ["city_id", "city_name", "temperature", "humidity", "pressure", "collected_at"]
    for col in required_columns:
        null_rows = df_pass[df_pass[col].isnull()]
        if not null_rows.empty:
            df_fail = pd.concat([df_fail, null_rows])
        df_pass = df_pass.dropna(subset=[col])

    # 2. Check data type for city_id (must be int)
    if not pd.api.types.is_integer_dtype(df_pass["city_id"]):
        non_int_rows = df_pass[~df_pass["city_id"].apply(lambda x: isinstance(x, int))]
        if not non_int_rows.empty:
            df_fail = pd.concat([df_fail, non_int_rows])
        df_pass = df_pass[df_pass["city_id"].apply(lambda x: isinstance(x, int))]

    # 3. Check valid ranges for numeric columns
    def filter_invalid_rows(column, min_val, max_val):
        nonlocal df_pass, df_fail
        invalid = df_pass[~df_pass[column].between(min_val, max_val, inclusive="both")]
        if not invalid.empty:
            df_fail = pd.concat([df_fail, invalid])
        df_pass = df_pass[df_pass[column].between(min_val, max_val, inclusive="both")]

    filter_invalid_rows("temperature", -50, 60)
    filter_invalid_rows("humidity", 0, 100)
    filter_invalid_rows("pressure", 800, 1100)
    if "wind_speed" in df_pass.columns:
        filter_invalid_rows("wind_speed", 0, 150)
    if "wind_direction" in df_pass.columns:
        filter_invalid_rows("wind_direction", 0, 360)
    if "cloud_cover" in df_pass.columns:
        filter_invalid_rows("cloud_cover", 0, 100)

    # 4. Check that collected_at time is within the last 5 minutes
    now = datetime.utcnow()
    time_threshold = now - timedelta(minutes=5)
    df_pass["collected_at"] = pd.to_datetime(df_pass["collected_at"], errors="coerce")
    invalid_time = df_pass[~df_pass["collected_at"].between(time_threshold, now)]
    if not invalid_time.empty:
        df_fail = pd.concat([df_fail, invalid_time])
    df_pass = df_pass[df_pass["collected_at"].between(time_threshold, now)]

    # 5. Check uniqueness of city_id (keep the first record)
    duplicated = df_pass[df_pass.duplicated("city_id", keep=False)]
    if not duplicated.empty:
        df_fail = pd.concat([df_fail, duplicated])
    df_pass = df_pass.drop_duplicates("city_id", keep="first")

    # 6. Convert collected_at column to string for JSON serialization
    if "collected_at" in df_pass.columns:
        df_pass["collected_at"] = df_pass["collected_at"].astype(str)
    if "collected_at" in df_fail.columns:
        df_fail["collected_at"] = df_fail["collected_at"].astype(str)

    return df_pass, df_fail
