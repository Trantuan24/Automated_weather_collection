import pandas as pd
from fetch_weather import get_weather_dataframe
from text_unidecode import unidecode

# Map city names for normalization
CITY_NAME_MAP = {
    "Turan": "Da Nang",
    "Qui Nhon": "Quy Nhon",
    "Ho Chi Minh City": "Ho Chi Minh",
}

def remove_accents(text):
    """Remove Vietnamese accents for consistent city names without diacritics."""
    return unidecode(text)

def clean_and_transform(df):
    """
    Clean and normalize weather data.
    """
    # Remove rows with missing important data
    df.dropna(subset=["city_id", "temperature", "humidity", "pressure"], inplace=True)

    # Convert data types
    df["collected_at"] = pd.to_datetime(df["collected_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["city_id"] = df["city_id"].astype(int)
    df["precipitation"] = df["precipitation"].fillna(0).astype(float)

    # Replace "N/A" with None for better handling
    df.replace("N/A", None, inplace=True)

    # Map city names
    df["city_name"] = df["city_name"].replace(CITY_NAME_MAP)
    df["city_name"] = df["city_name"].apply(remove_accents)

    # Remove outlier data
    df = df[(df["temperature"] >= -50) & (df["temperature"] <= 60)]
    df = df[(df["humidity"] >= 0) & (df["humidity"] <= 100)]

    return df

if __name__ == "__main__":
    raw_df = get_weather_dataframe() 
    clean_df = clean_and_transform(raw_df) 
    print(clean_df.head())  
