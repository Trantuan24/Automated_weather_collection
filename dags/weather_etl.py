from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from text_unidecode import unidecode
import pandas as pd
import os
import sys

# Add the scripts directory to PYTHONPATH to import modules
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../scripts"))

from fetch_weather import get_weather_dataframe
from transform_data import clean_and_transform
from data_quality_check import validate_data
from load_to_postgres import load_to_postgres
from save_to_json import save_to_json

# Set up DAG parameters
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 2, 25),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "weather_etl",
    default_args=default_args,
    description="ETL pipeline for processing weather data",
    schedule_interval="0 */6 * * *",
    catchup=False,
)

# Task 1: Fetch data from API
def fetch_weather():
    return get_weather_dataframe()

fetch_task = PythonOperator(
    task_id="fetch_weather",
    python_callable=fetch_weather,
    dag=dag,
)

# Task 2: Clean and transform data
def transform_data(**kwargs):
    ti = kwargs["ti"]
    raw_df = ti.xcom_pull(task_ids="fetch_weather")
    return clean_and_transform(raw_df)

transform_task = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

# Task 3: Data quality check
def data_quality(**kwargs):
    ti = kwargs["ti"]
    transformed_df = ti.xcom_pull(task_ids="transform_data")
    df_pass, df_fail = validate_data(transformed_df)
    return {"df_pass": df_pass.to_dict(), "df_fail": df_fail.to_dict()}

quality_task = PythonOperator(
    task_id="data_quality_check",
    python_callable=data_quality,
    provide_context=True,
    dag=dag,
)

# Task 4: Load data into PostgreSQL
def load_postgres(**kwargs):
    ti = kwargs["ti"]
    data = ti.xcom_pull(task_ids="data_quality_check")
    df_pass = pd.DataFrame.from_dict(data["df_pass"])
    df_fail = pd.DataFrame.from_dict(data["df_fail"])
    load_to_postgres(df_pass, "weather_data")
    load_to_postgres(df_fail, "invalid_weather_data")

load_postgres_task = PythonOperator(
    task_id="load_to_postgres",
    python_callable=load_postgres,
    provide_context=True,
    dag=dag,
)

# Task 5: Save valid data to JSON
def save_json(**kwargs):
    ti = kwargs["ti"]
    data = ti.xcom_pull(task_ids="data_quality_check")
    df_pass = pd.DataFrame.from_dict(data["df_pass"])
    save_to_json(df_pass)

save_json_task = PythonOperator(
    task_id="save_to_json",
    python_callable=save_json,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
fetch_task >> transform_task >> quality_task
quality_task >> [load_postgres_task, save_json_task]
