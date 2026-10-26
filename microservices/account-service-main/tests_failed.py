import requests
import jwt

BASE_URL = "http://127.0.0.1:6900"
JWT_SECRET = "SUPER_SECRET_ASDFASDFASDFASDEWQER"


def fail_create_account_1():
    payload = {
        "username": "",
        "password": "mypassword123"
    }

    response = requests.post(f"{BASE_URL}/accounts", json=payload)

    print("\n[#1 Test for failed case of creating an account]")
    print("Case: Missing username")

    print(f"Status Code: {response.status_code}")
    print(f"Response cBody: {response.json()}")

def fail_create_account_2():
    payload = {
        "username": "abc",
        "password": ""
    }

    response = requests.post(f"{BASE_URL}/accounts", json=payload)

    print("\n[#2 Test for failed case of creating an account]")
    print("Case: Missing password")
    print(f"Payload: {payload}")
    print("\nResult:")

    print(f"Status Code: {response.status_code}")
    print(f"Response cBody: {response.json()}")

def fail_create_account_3():
    payload1 = {
        "username": "abc",
        "password": "mypassword123"
    }
    payload2 = {
        "username": "def",
        "password": "mypassword456"
    }
    payload3 = {
        "username": "abc",
        "password": "anotherpassword123"
    }
    response1 = requests.post(f"{BASE_URL}/accounts", json=payload1)
    response2 = requests.post(f"{BASE_URL}/accounts", json=payload2)
    response3 = requests.post(f"{BASE_URL}/accounts", json=payload3)

    print("\n[#3 Test for failed case of creating an account]")
    print("\n Case: Username already exists")
    print("\nAccount created with username 'abc':")
    print(f"Payload: {payload1}")
    print("\nAccount created with username 'def':")
    print(f"Payload: {payload2}")
    print("\nUsername already exists:")
    print(f"Payload: {payload3}")
    print("\nResult:")
    print("\nAccount created with username 'abc':")
    print(f"Status Code: {response1.status_code}")
    print(f"Response cBody: {response1.json()}")
    print("\nAccount created with username 'def':")
    print(f"Status Code: {response2.status_code}")
    print(f"Response cBody: {response2.json()}")
    print("\nUsername already exists:")
    print(f"Status Code: {response3.status_code}")
    print(f"Response cBody: {response3.json()}")

def _helper_login(payload):
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
    
def fail_login_1():
    payload = {
        "username": "",
        "password": "mypassword123"
    }
    response = _helper_login(payload)

    print("\n[#1 Test for failed case of logging into an account]")
    print(f"Payload: {payload}")
    print("Case: Missing username")
    print("\nResult:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

    _helper_access_token(response)

def fail_login_2():
    payload = {
        "username": "abc",
        "password": ""
    }
    response = _helper_login(payload)

    print("\n[#2 Test for failed case of logging into an account]")
    print(f"Payload: {payload}")
    print("Case: Missing password")
    print("\nResult:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

    _helper_access_token(response)

def fail_login_3():
    payload = {
        "username": "abc",
        "password": "notmypassword123"
    }
    response = _helper_login(payload)

    print("\n[#3 Test for failed case of logging into an account]")
    print(f"Payload: {payload}")
    print("Case: Invalid password")
    print("\nResult:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

    _helper_access_token(response)

def fail_login_4():
    payload = {
        "username": "notauser",
        "password": "mypassword123"
    }
    response = _helper_login(payload)

    print("\n[#4 Test for failed case of logging into an account]")
    print(f"Payload: {payload}")
    print("Case: If the user is not found")
    print("\nResult:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

    _helper_access_token(response)


def fail_change_pw_1():
    print("\n[#1 Test for changing the password of an account]")
    payload_login = {
        "username": "abc",
        "password": "mypassword123"
    }
    payload = {
        "old_password": "mypassword123",
        "new_password": "updatedpassword123"
    }

    print(f"Payload for logging in: {payload_login}")
    print(f"Payload for changing password: {payload}")
    print("Case: Header does not exist")
    print("\nResult:")

    login_response = _helper_login(payload_login)
    access_token, decoded_access_token = _helper_access_token(login_response)

    if access_token and decoded_access_token:
        login_username = decoded_access_token.get("sub")

        response = requests.put(
            f"{BASE_URL}/accounts/{login_username}/change_password",
            json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")

def fail_change_pw_2():
    print("\n[#2 Test for changing the password of an account]")
    payload_login = {
        "username": "abc",
        "password": "mypassword123"
    }
    payload = {
        "old_password": "mypassword123",
        "new_password": "updatedpassword123"
    }

    print(f"Payload for logging in: {payload_login}")
    print(f"Payload for changing password: {payload}")
    print("Case: Header is not in JWT format")
    print("\nResult:")

    login_response = _helper_login(payload_login)
    access_token, decoded_access_token = _helper_access_token(login_response)

    if access_token and decoded_access_token:
        login_username = decoded_access_token.get("sub")
        login_headers = {
            "Authorization": f"{access_token}"
        }

        response = requests.put(
            f"{BASE_URL}/accounts/{login_username}/change_password",
            json=payload, headers=login_headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")

def fail_change_pw_3():
    print("\n[#3 Test for changing the password of an account]")
    payload_login = {
        "username": "abc",
        "password": "mypassword123"
    }
    payload = {
        "old_password": "mypassword123",
        "new_password": "updatedpassword123"
    }

    print(f"Payload for logging in: {payload_login}")
    print(f"Payload for changing password: {payload}")
    print("Case: Username does not match the current account")
    print("\nResult:")

    login_response = _helper_login(payload_login)
    access_token, decoded_access_token = _helper_access_token(login_response)

    if access_token and decoded_access_token:
        login_headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.put(
            f"{BASE_URL}/accounts/def/change_password",
            json=payload, headers=login_headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")

def fail_change_pw_4():
    print("\n[#4 Test for changing the password of an account]")
    payload_login = {
        "username": "abc",
        "password": "mypassword123"
    }
    payload = {
        "old_password": "mypassword123",
        "new_password": "updatedpassword123"
    }

    print(f"Payload for logging in: {payload_login}")
    print(f"Payload for changing password: {payload}")
    print("Case: Token is invalid")
    print("\nResult:")

    login_response = _helper_login(payload_login)
    access_token, decoded_access_token = _helper_access_token(login_response)

    if access_token and decoded_access_token:
        login_username = decoded_access_token.get("sub")
        login_headers = {
            "Authorization": f"Bearer {access_token}232"
        }

        response = requests.put(
            f"{BASE_URL}/accounts/{login_username}/change_password",
            json=payload, headers=login_headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")

def fail_change_pw_5():
    print("\n[#5 Test for changing the password of an account]")
    payload_login = {
        "username": "abc",
        "password": "mypassword123"
    }
    payload = {
        "old_password": "",
        "new_password": "updatedpassword123"
    }

    print(f"Payload for logging in: {payload_login}")
    print(f"Payload for changing password: {payload}")
    print("Case: Old password value is missing")
    print("\nResult:")

    login_response = _helper_login(payload_login)
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

def fail_change_pw_6():
    print("\n[#6 Test for changing the password of an account]")
    payload_login = {
        "username": "abc",
        "password": "mypassword123"
    }
    payload = {
        "old_password": "mypassword123",
        "new_password": ""
    }

    print(f"Payload for logging in: {payload_login}")
    print(f"Payload for changing password: {payload}")
    print("Case: New password value is missing")
    print("\nResult:")

    login_response = _helper_login(payload_login)
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

def fail_change_pw_7():
    print("\n[#7 Test for changing the password of an account]")
    payload_login = {
        "username": "abc",
        "password": "mypassword123"
    }
    payload = {
        "old_password": "mypassword456",
        "new_password": "updatedpassword123"
    }

    print(f"Payload for logging in: {payload_login}")
    print(f"Payload for changing password: {payload}")
    print("Case: Old password value is incorrect")
    print("\nResult:")

    login_response = _helper_login(payload_login)
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
    print("RESETTING DATABASE FOR FAILURE TESTS")
    print("="*80)
    try:
        requests.post(f"{BASE_URL}/test/reset") 
    except Exception:
        print("Could not reset database")

    test_funcs = [
        fail_create_account_1,
        fail_create_account_2,
        fail_create_account_3,
        fail_login_1,
        fail_login_2,
        fail_login_3,
        fail_login_4,
        fail_change_pw_1,
        fail_change_pw_2,
        fail_change_pw_3,
        fail_change_pw_4,
        fail_change_pw_5,
        fail_change_pw_6,
        fail_change_pw_7
        ]
    
    for test_func in test_funcs:
        test_func()
        print("\n" + "="*80)