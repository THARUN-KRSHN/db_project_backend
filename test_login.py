import urllib.request
import json

data = json.dumps({"email": "test789_dummy@gmail.com", "password": "password123"}).encode("utf-8")
req = urllib.request.Request("http://127.0.0.1:8000/auth/login", data=data, headers={"Content-Type": "application/json"})

try:
    resp = urllib.request.urlopen(req)
    res_data = json.loads(resp.read().decode('utf-8'))
    print("Login Success!")
    token = res_data["access_token"]
    
    # Verify with /auth/me
    req_me = urllib.request.Request(
        "http://127.0.0.1:8000/auth/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    resp_me = urllib.request.urlopen(req_me)
    print("Me API Success!", resp_me.read().decode("utf-8"))
    
except urllib.error.HTTPError as e:
    print(f"HTTPError {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
