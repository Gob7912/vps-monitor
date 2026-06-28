import os
import psutil
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

BASE_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')
USERNAME = os.getenv('API_USERNAME', 'demo')
PASSWORD = os.getenv('API_PASSWORD', 'demo123')
SERVER_ID = int(os.getenv('SERVER_ID', 3))

token = None


def login():
    global token
    url = f"{BASE_URL}/api/auth/login/"
    try:
        resp = requests.post(url, json={
            "username": USERNAME,
            "password": PASSWORD
        }, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            token = data['access']
            print(f"Logged in. Token obtained.")
        else:
            print(f"Login failed: {resp.status_code} {resp.text}")
            token = None
    except requests.exceptions.RequestException as e:
        print(f"Login error: {e}")
        token = None


def collect_metrics():
    return {
        "server": SERVER_ID,
        "cpu_usage": psutil.cpu_percent(interval=1),
        "ram_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }


def send_metrics():
    global token
    if not token:
        login()
        if not token:
            return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = collect_metrics()
    try:
        response = requests.post(f"{BASE_URL}/api/metrics/", json=data, headers=headers, timeout=10)
        if response.status_code == 401:
            print("Token expired. Re-logging in...")
            login()
        else:
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Send error: {e}")


if __name__ == "__main__":
    login()
    while True:
        send_metrics()
        time.sleep(10)
