import requests
import json

url = "http://127.0.0.1:6901/convert-unit"

test_cases = [
    # test lb <-> kg
    {"value": 10, "from_unit": "lb", "to_unit": "kg"},
    {"value": 10, "from_unit": "kg", "to_unit": "lb"},

    # test g <-> oz
    {"value": 1, "from_unit": "g", "to_unit": "oz"},
    {"value": 1, "from_unit": "oz", "to_unit": "g"},

    # Invalid requests
    {"value": 1, "from_unit": "g"},
    {"value": 1, "from_unit": "mg", "to_unit": "oz"},
    {}
]

for case in test_cases:
    response = requests.post(url, json=case)
    data = response.json()
    print("Case:", case)
    print("Status:", response.status_code)

    try:
        print(json.dumps(response.json(), indent=4))
    except:
        print("Response :", response.text)

    print("=" * 80)