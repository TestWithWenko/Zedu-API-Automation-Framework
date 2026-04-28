import pytest
import os
from faker import Faker
from dotenv import load_dotenv
from conftest import raw_login
from schemas.user_schema import (
    USER_PROFILE_SCHEMA,
    USER_UPDATE_SCHEMA,
)
from utils.validators import (
    assert_success,
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




def get_user_id():
    resp = raw_login()
    jsonData = resp.json()
    user_id = jsonData["data"]["user"]["id"]
    return user_id


# -----------POSITIVE TEST CASES---------------
class TestUser:
    
    def test_user_get_own_profile(self, authenticated_api):
        user_id = get_user_id()
        resp = authenticated_api.get(f"/users/{user_id}")
        jsonData = assert_success(resp, 200)
        
        assert_fields_present(jsonData, ["status", "status_code", "message", "data"])
        
        assert_fields_present(jsonData["data"], [
            "id", "email", "name", "is_active",
        ])
        
        assert_field_types(jsonData, {
            "status":      str,
            "status_code": int,
            "message":     str,
            "data":        dict,
        })
        
        assert_field_types(jsonData["data"], {
            "id":        str,
            "email":     str,
            "name": str,
            "is_active":  bool,
        })
        
        assert_field_value(jsonData, {"status": "success"})
        
        assert len(jsonData["data"]["id"]) > 0, "User id should not be empty"
        assert_schema(jsonData, USER_PROFILE_SCHEMA)
    
    
    @pytest.mark.xfail(
        reason=(
            "API DEFECT: PUT /user/{userId} returns 200 with empty body. Correct behaviour should be either: 204 No Content with no body, OR 200 OK with the updated user object returned"
        ),
        strict=True  
    )
    
    def test_update_user_details(self, authenticated_api):
        user_id = get_user_id()
        new_first_name = fake.first_name()
        new_last_name = fake.last_name()
        new_user_name = fake.user_name()
        
        resp = authenticated_api.put(f"/users/{user_id}", json = {"first_name": new_first_name, "last_name": new_last_name, "username": new_user_name,})
        
        assert resp.status_code == 200
        
        jsonData = resp.json()
        assert_fields_present(jsonData, ["status", "status_code", "message", "data"])
        
        assert_schema(jsonData, USER_UPDATE_SCHEMA)
   
        
       
        
        
        

# --------------NEGATIVE TEST CASES------------------
class TestUserNegative:
    
    def test_get_user_profile_without_token(self, unauthenticated_api):
        resp = unauthenticated_api.get("/users/me")
        assert_error(resp, 401)
        
    def test_get__user_profile_of_non_existent_user(self, authenticated_api):
        resp = authenticated_api.get(f"/users/{fake.uuid4()}")
        assert resp.status_code in [400, 401, 403, 422], (
            f"Expected 400 or 401; Actual Response: {resp.status_code}"
        )
        assert_error(resp, 400)
        
    def test_update_user_profile_without_token(self, unauthenticated_api):
        user_id = get_user_id()
        new_first_name = fake.first_name()
        new_last_name = fake.last_name()
        new_user_name = fake.user_name()
        
        resp = unauthenticated_api.put(f"/users/{user_id}", json = {"first_name": new_first_name, "last_name": new_last_name, "username": new_user_name,})
        
        assert_error(resp, 401)
        
        
        
    # ----------------------------EGDE CASES---------------------------------------  
        
class TestUserEdge:
    def test_update_last_name_with_empty_string(self,authenticated_api):
        user_id = get_user_id()
        resp = authenticated_api.put(f"/users/{user_id}", json={"firstName": ""})
        
        assert_no_server_error(resp)
        assert resp.status_code in [400, 401, 422]
        assert_error(resp, 422)
        
    def test_update_first_name_as_integer(self, authenticated_api):
        user_id = get_user_id()
        resp = authenticated_api.put(f"/users/{user_id}", json={"firstName": fake.phone_number()})
        
        assert_no_server_error(resp)
        assert resp.status_code in [400,401, 422]
        assert_error(resp, 422)
        
    def test_update_with_extra_unknown_fields(self, authenticated_api):
        user_id = get_user_id()
        resp = authenticated_api.put(f"/users/{user_id}", json={"unknown": fake.name()})
        
        assert_no_server_error(resp)
        assert resp.status_code in [400,401, 422]
        assert_error(resp, 422)