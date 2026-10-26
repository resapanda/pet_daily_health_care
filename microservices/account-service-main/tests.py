import requests
import jwt

BASE_URL = "http://127.0.0.1:6900"
JWT_SECRET = "SUPER_SECRET_ASDFASDFASDFASDEWQER"


def test_create_account():
    payload = {
        "username": "abc",
        "password": "mypassword123"
    }

    response = requests.post(f"{BASE_URL}/accounts", json=payload)

    print("[Test for creating an account]")
    print(f"Status Code: {response.status_code}")
    print(f"Response cBody: {response.json()}")


def _helper_login():
    payload = {
        "username": "abc",
        "password": "mypassword123"
    }

    response = requests.post(f"{BASE_URL}/login", json=payload)
    return response


def _helper_access_token(response):
    if response.status_code == 200:
        body = response.json()
        access_token = body.get("access_token")

        decoded_access_token = jwt.decode(access_token, JWT_SECRET,
                                          algorithms=["HS256"])
        print(f"decoded jwt payload: {decoded_access_token}")
        return (access_token, decoded_access_token)


def test_login():
    response = _helper_login()

    print("\n[Test for logging into an account]")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

    _helper_access_token(response)


def test_change_pw():
    print("\n[Test for changing the password of an account]")
    payload = {
        "old_password": "mypassword123",
        "new_password": "updatedpassword123"
    }

    login_response = _helper_login()
    access_token, decoded_access_token = _helper_access_token(login_response)

    if access_token and decoded_access_token:
        login_username = decoded_access_token.get("sub")
        login_headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.put(
            f"{BASE_URL}/accounts/{login_username}/change_password",
            json=payload, headers=login_headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RESETTING DATABASE FOR TESTS")
    print("="*80 +"\n")
    try:
        requests.post(f"{BASE_URL}/test/reset") 
    except Exception:
        print("Could not reset database")

    test_funcs = [
        test_create_account,
        test_login,
        test_change_pw
    ]

    for test_func in test_funcs:
        test_func()
        print("\n" + "="*80)
