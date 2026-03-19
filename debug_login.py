import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    url = f"{BASE_URL}/auth/login"
    # Use a dummy or known user if possible, but the 400 error suggests a code failure
    payload = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    print(f"Testing login at {url}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_login()
