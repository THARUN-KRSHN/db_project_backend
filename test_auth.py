import urllib.request
import json
import urllib.error

data = json.dumps({"email": "test456_dummy@gmail.com", "password": "password123", "full_name": "Test User"}).encode("utf-8")
req = urllib.request.Request("http://127.0.0.1:8000/auth/register", data=data, headers={"Content-Type": "application/json"})

try:
    urllib.request.urlopen(req)
    print("Success")
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode("utf-8"))
except Exception as e:
    print(f"Error: {e}")
