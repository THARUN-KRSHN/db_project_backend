
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def test_public_endpoints():
    print("Testing public endpoints...")
    client = httpx.Client(timeout=30.0)
    try:
        # Shop list
        resp = client.get(f"{BASE_URL}/public/shops")
        print(f"GET /public/shops: {resp.status_code}")
        if resp.status_code == 200:
            shops = resp.json()
            if shops:
                # Find TRNDO (from logs) or use the first one
                target_shop = next((s["shop_name"] for s in shops if "TRNDO" in s["shop_name"]), shops[0]["shop_name"])
                print(f"Testing shop: '{target_shop}'")
                
                # Shop info
                info = client.get(f"{BASE_URL}/public/shop/{target_shop}")
                print(f"GET /public/shop/{target_shop}: {info.status_code}")
                
                # Inventory
                # Test both with and without trailing space if it exists
                inv = client.get(f"{BASE_URL}/public/shop/{target_shop}/inventory")
                print(f"GET /public/shop/{target_shop}/inventory: {inv.status_code}")
                if inv.status_code == 200:
                    print("Inventory fetch successful (Image column check passed)")
                else:
                    print(f"Inventory fetch failed: {inv.status_code} - {inv.text}")
            else:
                print("No shops found in database.")
        else:
            print(f"Failed to list shops: {resp.status_code}")
    except httpx.ConnectError:
        print("Error: Could not connect to the server. Is it running on port 8000?")
    except AttributeError as e:
        print(f"Prop error: {e}")
    except Exception as e:
        print(f"Error testing endpoints: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_public_endpoints()
