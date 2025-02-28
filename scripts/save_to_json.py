import os
import json
import pandas as pd
from datetime import datetime, timedelta

def save_to_json(df_pass):
    """
    Save valid data to a JSON Lines (.jsonl) file, organized by month/day.
    """
    if df_pass.empty:
        print("⚠ No valid data to save.")
        return

    # Define the folder structure and file name
    now = datetime.utcnow()
    month_folder = now.strftime("%Y-%m")
    day_file = now.strftime("%Y-%m-%d.jsonl")
    save_dir = os.path.join("data", month_folder)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, day_file)
    
    # Save data as JSON Lines (.jsonl)
    with open(file_path, "a", encoding="utf-8") as f:
        for record in df_pass.to_dict(orient="records"):
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    print(f"✅ Saved {len(df_pass)} records to {file_path}")


def cleanup_old_files():
    """
    Delete JSON data older than 30 days to avoid taking up space.
    """
    base_dir = "data"
    if not os.path.exists(base_dir):
        return
    
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    for month_folder in os.listdir(base_dir):
        month_path = os.path.join(base_dir, month_folder)
        if os.path.isdir(month_path):
            for file_name in os.listdir(month_path):
                file_path = os.path.join(month_path, file_name)
                try:
                    file_date = datetime.strptime(file_name.replace(".jsonl", ""), "%Y-%m-%d")
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        print(f"🗑 Deleted {file_path}")
                except ValueError:
                    continue  

if __name__ == "__main__":
    from fetch_weather import get_weather_dataframe
    from transform_data import clean_and_transform
    
    raw_df = get_weather_dataframe()
    df_pass = clean_and_transform(raw_df)
    save_to_json(df_pass)
    cleanup_old_files()
