import requests
import json

BASE_URL = "http://127.0.0.1:6901"

test_cases = [
    # --- Unit Conversions (/convert-unit) ---
    {"endpoint": "/convert-unit", "payload": {"value": 10, "from_unit": "lb", "to_unit": "kg"}},
    {"endpoint": "/convert-unit", "payload": {"value": 10, "from_unit": "kg", "to_unit": "lb"}},
    {"endpoint": "/convert-unit", "payload": {"value": 1, "from_unit": "g", "to_unit": "oz"}},
    {"endpoint": "/convert-unit", "payload": {"value": 1, "from_unit": "oz", "to_unit": "g"}},
    {"endpoint": "/convert-unit", "payload": {"value": 1, "from_unit": "g"}}, # Invalid
    {"endpoint": "/convert-unit", "payload": {"value": 1, "from_unit": "mg", "to_unit": "oz"}}, # Invalid

    # --- Time Conversions (/convert-time) ---
    {"endpoint": "/convert-time", "payload": {"twelveHourTime": "12:00 AM"}},
    {"endpoint": "/convert-time", "payload": {"twentyFourHourTime": "00:00"}},
    {"endpoint": "/convert-time", "payload": {"twelveHourTime": "1:05 ZM"}}, # Invalid
    
    # --- Edge Cases ---
    {"endpoint": "/convert-unit", "payload": {}},
    {"endpoint": "/convert-time", "payload": {"mumbo": 23, "jumbo": 87}}
]

def run_test():
    for i, test in enumerate(test_cases, 1):
        url = f"{BASE_URL}{test['endpoint']}"
        payload = test['payload']
        
        print(f"Test #{i}: POST to {url}")
        print(f"Payload: {payload}")
        
        try:
            response = requests.post(url, json=payload)
            print(f"Status: {response.status_code}")

            try:
                print("Response:", json.dumps(response.json(), indent=4))
            except:
                print("Response (Text):", response.text)
                
        except requests.exceptions.ConnectionError:
            print("FAILED: Server is not running at", BASE_URL)
            break
            
        print("=" * 80)

if __name__ == "__main__":
    run_test()