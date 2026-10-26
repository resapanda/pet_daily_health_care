import requests

URL = "http://127.0.0.1:6901/convert-time"

test_cases = [
    # Valid 12 hr to 24 hr time conversions
    {"twelveHourTime": "12:00 AM"},
    {"twelveHourTime": "11:59 PM"},
    {"twelveHourTime": "12:01 AM"},
    {"twelveHourTime": "2:46 PM"},

    # Valid 24 to 12 hr time conversions
    {"twentyFourHourTime": "00:00"},
    {"twentyFourHourTime": "23:59"},
    {"twentyFourHourTime": "00:05"},
    {"twentyFourHourTime": "14:50"},

    # invalid requests
    {"twelveHourTime": "13:05 PM"},
    {"twentyFourHourTime": "24:06"},
    {"twelveHourTime": "2:00 PM", "twentyFourHourTime": "14:00"},
    {"twelveHourTime": "1:05 ZM"},
    {},
    {"mumbo": 23, "jumbo": 87}
]

for case in test_cases:
    response = requests.post(URL, json=case)
    print("Status:", response.status_code)

    try:
        print("Response:", response.json())
    except:
        print("Response text:", response.text)

    print("=" * 80)