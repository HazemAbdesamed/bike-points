import requests
import json
import os
import time

# Superset URL and credentials
SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"  # Adjust according to your setup
PASSWORD = "admin"  # Adjust according to your setup

# Dataset information
DATABASE_NAME = "presto"  # The name you gave when you connected Trino in Superset
SCHEMA = "default"        # Schema name in Trino
TABLE_NAME = "metrics"    # The Kafka table name
DATASET_NAME = "trino_view_dataset"  # Name you want for the dataset

# Log in to Superset and get an access token
def get_access_token():
    login_url = f"{SUPERSET_URL}/api/v1/security/login"
    headers = {"Content-Type": "application/json"}
    payload = {"username": USERNAME, "password": PASSWORD, "provider": "db"}
    response = requests.post(login_url, headers=headers, json=payload)
    response_data = response.json()
    return response_data["access_token"]

# Get the database ID
def get_database_id(token):
    databases_url = f"{SUPERSET_URL}/api/v1/database/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(databases_url, headers=headers)
    databases = response.json()["result"]
    for db in databases:
        if db["database_name"] == DATABASE_NAME:
            return db["id"]
    raise Exception("Database not found")

# Create the dataset
def create_dataset(token, database_id):
    datasets_url = f"{SUPERSET_URL}/api/v1/dataset/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "database": database_id,
        "schema": SCHEMA,
        "table_name": TABLE_NAME,
        "sql": """
            SELECT 
              from_iso8601_timestamp(json_extract_scalar(_message, '$.min_extraction_datetime')) AS min_extraction_datetime,
              from_iso8601_timestamp(json_extract_scalar(_message, '$.max_extraction_datetime')) AS max_extraction_datetime,
              json_extract_scalar(_message, '$.percentage_available_bikes') AS percentage_available_bikes,
              json_extract_scalar(_message, '$.nb_in_use_bikes') AS nb_in_use_bikes,
              json_extract_scalar(_message, '$.percentage_in_use_bikes') AS percentage_in_use_bikes,
              json_extract_scalar(_message, '$.nb_broken_docks') AS nb_broken_docks,
              json_extract_scalar(_message, '$.percentage_broken_docks') AS percentage_broken_docks
            FROM kafka.default.metrics
            WHERE _message <> '{}'
        """,
        "table_name": DATASET_NAME,
        "is_managed_externally": False
    }
    response = requests.post(datasets_url, headers=headers, json=payload)
    if response.status_code == 201:
        print("Dataset created successfully!")
    else:
        print(f"Error creating dataset: {response.content}")

if __name__ == "__main__":
    time.sleep(15)  # Wait for Superset to be ready
    token = get_access_token()
    database_id = get_database_id(token)
    create_dataset(token, database_id)
