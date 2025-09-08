import requests
import time

# Wait a moment for server to start
time.sleep(2)

try:
    response = requests.get("http://localhost:8000/health")
    print(f"Health check status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Health check failed: {e}")

try:
    response = requests.get("http://localhost:8000/")
    print(f"Root endpoint status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Root endpoint failed: {e}")
