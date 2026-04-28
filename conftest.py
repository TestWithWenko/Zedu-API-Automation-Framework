import pytest
import requests
import os
from dotenv import load_dotenv
from utils.api_client import ApiClient

load_dotenv()

print("BASE_URL =", os.getenv("BASE_URL"))

BASE_URL = os.getenv("BASE_URL")
test_email = os.getenv("TEST_EMAIL")
test_password = os.getenv("TEST_PASSWORD")

def raw_login(email = None, password = None):
    payload = {
        "email": email if email is not None else test_email,
        "password": password if password is not None else test_password,
    }
    return requests.post(
        f"{BASE_URL}/auth/login",
        json = payload,
        headers = {"Content-Type": "application/json"}
    )
    
    
@pytest.fixture(scope="session")
def base_url():        
    return BASE_URL 


@pytest.fixture(scope = "session")
def auth_token():
    response = raw_login()
    
    assert response.status_code == 200, (
        f"Session login failed ({response.status_code}): {response.text}"
    )
    
    jsonData = response.json()
    
    token = (jsonData.get("data") or {}).get("access_token")
    
    assert token, (
        f"Token not present in the login response body. Response Body: {jsonData}"
    )
    return token


@pytest.fixture(scope="session")
def authenticated_api(auth_token):
    return ApiClient(token = auth_token)


@pytest.fixture(scope="session")
def unauthenticated_api():
    return ApiClient()


@pytest.fixture(scope = "session")
def base_url():
    return base_url