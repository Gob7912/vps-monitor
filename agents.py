import os
import psutil
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

api_url = os.getenv('API_URL', 'http://127.0.0.1:8000')
login_name = os.getenv('API_USERNAME', 'demo')
login_pass = os.getenv('API_PASSWORD', 'demo123')
server_id = int(os.getenv('SERVER_ID', 3))

my_token = None

def get_token():
    global my_token
    url = f"{api_url}/api/auth/login/"
    try:
        r = requests.post(url, json={
            "username": login_name,
            "password": login_pass
        }, timeout=10)
        if r.status_code == 200:
            data = r.json()
            my_token = data['access']
            print("Token ok")
        else:
            print(f"Login error: {r.status_code} {r.text}")
            my_token = None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        my_token = None


def get_data():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return {
        "server": server_id,
        "cpu_usage": cpu,
        "ram_usage": ram,
        "disk_usage": disk
    }

def send():
    global my_token
    if not my_token:
        get_token()
        if not my_token:
            return
    headers = {
        "Authorization": f"Bearer {my_token}",
        "Content-Type": "application/json"
    }
    data = get_data()
    try:
        r = requests.post(f"{api_url}/api/metrics/", json=data, headers=headers, timeout=10)
        if r.status_code == 401:
            print("Token expired")
            get_token()
        else:
            print(f"Status: {r.status_code}")
            print(f"Response: {r.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error send: {e}")


if __name__ == "__main__":
    get_token()
    while True:
        send()
        time.sleep(10)
