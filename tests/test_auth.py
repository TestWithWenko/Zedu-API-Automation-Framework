import requests
import os
from faker import Faker
from dotenv import load_dotenv
from conftest import raw_login
from schemas.auth_schema import (
    LOGIN_SUCCESS_SCHEMA,
    REGISTER_SUCCESS_SCHEMA,
    LOGOUT_SUCCESS_SCHEMA,
    ONBOARD_STATUS_SCHEMA,
    ERROR_SCHEMA,
)
from utils.validators import (
    assert_success,
    assert_success_2xx,
    assert_error,
    assert_schema,
    assert_field_types,
    assert_field_value,
    assert_fields_present,
    assert_no_server_error,
)

load_dotenv()

fake = Faker()
base_url = os.getenv("BASE_URL")
test_password = os.getenv("TEST_PASSWORD")


# -------------------------------POSITIVE TEST CASES---------------------------------

class TestValidRegistration:
    
    def test_valid_registration(self, unauthenticated_api):
        payload = {
            "username": fake.user_name(),
            "email": fake.unique.email(),
            "password": test_password,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": fake.phone_number(),
        }
        response = unauthenticated_api.post("/auth/register", json = payload)
        
        jsonData = assert_success(response, 201)
        
        assert_fields_present(jsonData, ["status", "status_code", "message", "data"])
        
        assert_field_types(jsonData, {
            "status": str,
            "status_code": int,
            "message": str,
            "data": dict,
        })
        
        assert_field_value(jsonData, {
            "status": "success",
            "message": "User Created Successfully"
        })
        
        assert_field_value(jsonData["data"]["user"], {
            "email": payload["email"]
        })
        
        assert_schema(jsonData, REGISTER_SUCCESS_SCHEMA)
        
        
        
        
        
class TestValidLogin:
    
    def test_valid_login(self):
        resp = raw_login()
        jsonData = assert_success(resp, 200)
        
        assert_fields_present(jsonData, ["status", "status_code", "message", "data"])
        
        assert_fields_present(jsonData["data"], ["access_token"])
        
        assert_field_types(jsonData, {
            "status":      str,
            "status_code": int,
            "message":     str,
            "data":        dict,
        })
        
        assert_field_types(jsonData["data"], {
            "access_token":       str,
        })
        
        token = jsonData["data"]["access_token"]
        assert len(token) > 20, (
            f"Access token looks too short to be valid: '{token}'"
        )
        
        assert_field_value(jsonData, {
            "status": "success",
            "message": "user login successfully",
        })
        assert_schema(jsonData, LOGIN_SUCCESS_SCHEMA)
        
        

class TestValidOnboardStatus:
    
    def test_valid_onboard_status(self, authenticated_api):
        resp = authenticated_api.get("/auth/onboard-status")
        jsonData = assert_success(resp, 200)
        
        assert_fields_present(jsonData, ["status", "status_code", "message", "data"])
        assert_fields_present(jsonData["data"], ["online", "status"])
        assert_field_types(jsonData, {
            "status":      str,
            "status_code": int,
            "message":     str,
            "data":        dict
        })        
        assert_field_types(jsonData["data"], {
            "online": bool,
            "status": bool,
        })       
        assert_field_value(jsonData, {
            "status": "success"
        })
        assert isinstance(jsonData["data"]["status"], bool), (
            "status must be a boolean"
        )       
        assert_schema(jsonData, ONBOARD_STATUS_SCHEMA)
        
        

class TestValidLogout:
    
    def test_valid_logout(self):
        
        freshLogin = raw_login()
        assert freshLogin.status_code == 200
        freshToken = freshLogin.json()["data"]["access_token"]
        
        from utils.api_client import ApiClient
        freshClient = ApiClient(token=freshToken)
        resp = freshClient.post("/auth/logout")
        
        jsonData = assert_success(resp, 200)
        
        assert_fields_present(jsonData, ["status", "status_code", "message"])
        
        assert_field_types(jsonData, {
            "status": str,
            "message": str
        })
        
        assert_field_value(jsonData, {
            "status": "success",
            "message": "user logout successfully"
        })
        
        assert_schema(jsonData, LOGOUT_SUCCESS_SCHEMA)
        
        
        
        
# ----------------------------Negative test cases------------------------------

class TestNegativeAuthCases:
    def test_login_with_wrong_password(self):
        resp = raw_login(password = fake.password())
        assert_error(resp, 401)
    
        
    def test_login_with_unregistered_email(self):
        resp = raw_login(email = fake.email())
        assert_error(resp, 401)
        
    def test_login_with_empty_password(self):
        resp = raw_login(password = "")
        assert_error(resp, 400)
    
    def test_login_with_empty_email(self):
        resp = raw_login(email = "")
        assert_error(resp, 400)
        
    def test_login_with_malformed_email(self):
        resp = raw_login(email = fake.email().replace("@",""))
        assert_error(resp, 400)
        
    def test_registration_with_duplicate_email(self, unauthenticated_api):
        email = fake.unique.email()
        payload = {
            "username": "Wenko",
            "email": email,
            "password": test_password,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": fake.phone_number()
        }
        
        firstResp = unauthenticated_api.post("/auth/register", json=payload)
        jsonData = assert_success(firstResp, 201)
        assert_fields_present(jsonData, ["message"])
        assert_field_types(jsonData, {"message": str})
        
        secondResp = unauthenticated_api.post("/auth/register", json=payload)
        assert secondResp.status_code == 400, (
            f"Duplicate registration should be rejected...Actual response: {secondResp.text}"
        )
        assert_error(secondResp, 400)
        
        
    def test_registration_with_missing_email_field(self, unauthenticated_api):
        payload = {
            "username": fake.user_name(),
            "password": test_password,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": fake.phone_number()
        }
        resp = unauthenticated_api.post("/auth/register", json = payload)
        assert resp.status_code == 422, (
            f"First registration failed unexpectedly: {resp.text}"
        )
        assert_error(resp, 422)
    
    def test_registration_with_malformed_email_field(self, unauthenticated_api):
        payload = {
            "username": fake.user_name(),
            "email": fake.unique.email().replace("@",""),
            "password": test_password,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": fake.phone_number()
        }
        resp = unauthenticated_api.post("/auth/register", json = payload)
        assert resp.status_code in (400, 422), (
            f"Registration failed unexpectedly: {resp.text}"
        )
        assert_error(resp, 400)   
    
    def test_registration_with_missing_password_field(self, unauthenticated_api):
        payload = {
            "username": fake.user_name(),
            "email": fake.unique.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": fake.phone_number()
        }
        resp = unauthenticated_api.post("/auth/register", json = payload)
        assert resp.status_code == 422, (
            f"First registration failed unexpectedly: {resp.text}"
        )
        assert_error(resp, 422)
        
        
    def test_onboard_status_route_without_token(self, unauthenticated_api):
        resp = unauthenticated_api.get("/auth/onboard-status")
        assert_error(resp, 401)
        
    
    def test_onboard_status_route_with_malformed_token(self, unauthenticated_api):
        resp = unauthenticated_api.get("/auth/onboard-status", headers = {"Authorization": f"Bearer {fake.uuid4()}"})
        assert_error(resp, 401)
    
    def test_logout_without_token(self, unauthenticated_api):
        resp = unauthenticated_api.post("/auth/logout")
        assert resp.status_code in [400, 401, 422], (
            f"Expected 400, 401 or 422 , Actual Response: {resp.status_code}"
        )
        assert_error(resp, 401)
      
        
        
# ------------------------------------EDGE CASES---------------------------------------------
class TestEdgeAuthCases:
    
    def test_login_extremely_long_password_does_not_crash_server(self):
        resp = raw_login(f"password={fake.password()* 1000}") 
        assert_no_server_error(resp)
        assert resp.status_code in [401, 422]
        assert_error(resp, 400)
        
    def test_login_with_form_encoded_body_does_not_crash_server(self):
        resp = requests.post(
            f"{base_url}/auth/login",
            data={
                "email":    os.getenv("TEST_EMAIL"),
                "password": os.getenv("TEST_PASSWORD"),
            }
        )
        assert_no_server_error(resp)
        assert resp.status_code in [400, 415, 422, 200]
        assert_error(resp, 400)
        
    def test_login_with_empty_body(self, unauthenticated_api):
        resp = unauthenticated_api.post("/auth/register", json={})
        assert_no_server_error(resp)
        assert resp.status_code in [400, 422]

        assert_error(resp, 422)
        
    def test_login_rejects_sql_injection_email(self):
        resp = raw_login(email="' OR '1'='1'; DROP TABLE users; --")
        assert_no_server_error(resp)
        assert resp.status_code in [400, 401, 422]

        jsonData = resp.json()
        assert_fields_present(jsonData, ["message"])
        assert_field_types(jsonData, {"message": str})
        assert jsonData["message"].strip() != ""
        
    def test_registration_with_unicode_character_in_first_name(self, unauthenticated_api):
        payload = {
            "username": "Wenko",
            "email": fake.unique.email(),
            "password": test_password,
            "first_name": "语桐",
            "last_name": fake.last_name(),
            "phone_number": fake.phone_number()
        }
        
        resp = unauthenticated_api.post("/auth/register", json=payload)
        jsonData = assert_success(resp, 201)
        assert_no_server_error(resp)
        assert_fields_present(jsonData, ["message"])
        assert_field_types(jsonData, {"message": str})
        
        