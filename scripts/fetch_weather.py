import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load API_KEY from .env file
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"

CITIES = ["Ha Noi", "Ho Chi Minh", "Da Nang", "Hai Phong", "Nha Trang", 
          "Can Tho", "Vinh", "Hue", "Buon Ma Thuot", "Da Lat",
          "Quy Nhon", "Pleiku", "Thanh Hoa", "Thai Nguyen", "Bac Ninh",
          "Phan Thiet", "My Tho", "Rach Gia", "Ha Long", "Ca Mau"]

def fetch_weather_data(city):
    """
    Call OpenWeather API to get the weather data of a city.
    """
    try:
        url = f"{BASE_URL}appid={API_KEY}&q={city},VN&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return {
            "city_id": data["id"],  
            "city_name": data["name"],  
            "country": data["sys"]["country"], 
            "collected_at": pd.Timestamp.now(), 
            "temperature": data["main"]["temp"],  
            "feels_like": data["main"]["feels_like"], 
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"], 
            "wind_speed": data["wind"]["speed"], 
            "wind_direction": data["wind"]["deg"], 
            "cloud_cover": data["clouds"]["all"], 
            "weather": data["weather"][0]["description"], 
            "visibility": data.get("visibility", "N/A"), 
            "dew_point": data["main"].get("dew_point", "N/A"),  
            "precipitation": data.get("rain", {}).get("1h", 0)  
        }
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching data for {city}: {e}")
        return None

def get_weather_dataframe():
    """
    Get weather data for the list of cities and return a DataFrame.
    """
    weather_data = [fetch_weather_data(city) for city in CITIES]
    weather_data = [data for data in weather_data if data]  
    return pd.DataFrame(weather_data)


