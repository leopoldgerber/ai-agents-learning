import time
import json
import requests


# Invalid data format
data = "not a json"
try:
    json_data = json.loads(data)
except ValueError as e:
    print("Invalid data format:", e)


# Missing data
def fetch_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 404:
        print("Data not found")
    return response.json() if response.status_code == 200 else None


# Outdated data
def validate_data(data):
    if "last_updated" in data and data["last_updated"] < "2020-01-01":
        print("Data is outdated")


# Performance issues
def process_large_data(data):
    start_time = time.time()
    time.sleep(2)  # Simulate processing
    print("Processing time:", time.time() - start_time)
