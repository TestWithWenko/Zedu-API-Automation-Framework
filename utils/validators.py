from jsonschema import validate, ValidationError
import pytest
import logging

logger = logging.getLogger(__name__)



def assert_status(response, expected_status):
    logger.info(f"Expected status: {expected_status} | Actual status: {response.status_code}")
    assert response.status_code == expected_status, (
        f"\n Expected Status: {expected_status}"
        f"\n Actual Status: {response.status_code}"
        f"\n Response Body: {response.text[:1000]}"
        f"\n Endpoint: {response.url}"
    )
    logger.info(f"Status code validated successfully: {response.status_code}")
    
    
def assert_success(response, expected_status = 200):
    assert_status(response, expected_status)
    try:
        jsonData = response.json()
        logger.info(f"Response is a valid Json")
    except Exception:
        pytest.fail(f"Response is not a valid JSON: {response.text}")
    return jsonData
    
    
def assert_success_2xx(response, expected_statuses = (200,201)):
    assert response.status_code in expected_statuses, (
        f"\n Expected one of {expected_statuses}"
        f"\n Actual response: {response.status_code}"
        f"\n Response body: {response.text}"
    )
    logger.info(f"Status code is validated successfully: {response.status_code} ")
    try:
        jsonData = response.json()
        logger.info(f"Response is a valid Json")
    except Exception:
        pytest.fail(f"Response is not a valid JSON: {response.text}")
    return jsonData
 
 
def assert_fields_present(jsonData: dict, fields: list):
    assert jsonData is not None, (
        "assert_field_present received no value"
    )
    logger.info(f"Checking field presence for: {fields}")
    for field in fields:
        assert field in jsonData, (
            f"Expected field '{field}' not found in the response body. Actual Field vailable: {list(jsonData.keys())}"
        )
        logger.info(f"Field '{field} ' is present")


def assert_field_types(jsonData: dict, type_map: dict):
    logger.info(f"Checking data type for: {list(type_map.keys())}")
    for field, expected_type in type_map.items():
        assert field in jsonData, f"Field '{field}' is missing from the response body"
        assert isinstance(jsonData[field], expected_type), (
            f"Field '{field}' should be {expected_type.__name__}, "
            f"Actual Result is {type(jsonData[field]).__name__}: {jsonData[field]}"
        )
        logger.info(
        F"{field} is {expected_type.__name__}"
        f"(value: {str(jsonData[field])[:60]})"
    )   


def assert_field_value(jsonData: dict, expectations: dict):
    logger.info(f"Checking field values for: {list(expectations.keys())}")
    for field, expected_value in expectations.items():
        assert field in jsonData, f"Field '{field}' not found in response"
        assert jsonData[field] == expected_value, (
            f" Expected Field Value:{field}'{expected_value}', Actual value: {jsonData[field]}'"
        )
        logger.info(f"'{field}' -- '{expected_value}' validated successfully")            


def assert_schema(jsonData, schema):
    logger.info(f"Validating response against schema")
    try:
        validate(instance=jsonData, schema = schema)
        logger.info(f"Schema validation passed")
    except ValidationError as ex:
        pytest.fail(
            f"\n Schema Validation failed"
            f"\n Failure Reason: {ex.message}"
        )


def assert_error(response, expected_status):
    logger.info(f"Expected error status code: {expected_status} | Actual status: {response.status_code}")
    assert response.status_code == expected_status, (
        f"\n Expected Status: {expected_status}"
        f"\n Actual Status: {response.status_code}"
        f"\n Response Body: {response.text}"
        f"\n Endpoint: {response.url}"
    )
    logger.info(f"Error status {response.status_code} validated successfully")
    try:
        jsonData  = response.json()
    except Exception:
        pytest.fail(f"Error response is not a valid JSON. Actual response Body: {response.text} ")
    logger.info(f"Checking [status, status_code, message] field exists")
    assert "status" in jsonData, (
        f"Error response missing status field."
    )
    assert "status_code" in jsonData, (
        f"Error response missing status_code field."
    )
    assert "message" in jsonData, (
        f"Error response missing message field."
    )
    logger.info(f"Status field is present")
    logger.info(f"Status_code field is present")
    logger.info(f"Message field is present")
    
    logger.info(f"Checking field type")
    assert isinstance(jsonData["status"], str),(
        f"Status should be a string, but Actual ype is: {type(jsonData['status'])}"
    )
    assert isinstance(jsonData["status_code"], int),(
        f"status_code should be an integer, but Actual type is: {type(jsonData['status_code'])}"
    )
    assert isinstance(jsonData["message"], str),(
        f"Message should be a string, but Actual type is: {type(jsonData['message'])}"
    )
    logger.info(f"Status Field value is a string")
    logger.info(f"Status_code Field value is an integer")
    logger.info(f"Message Field value is a string")
    
    if "error" in jsonData:
        assert isinstance(jsonData["error"], (str, dict)), (
            f"'error' field should be a string or object, "
            f"Actual response type {type(jsonData['error'])}"
        )
        logger.info(
            f"'error' is {type(jsonData['error']).__name__}: "
            f"{str(jsonData['error'])[:60]}"
        )
    logger.info(f"Checking the field has value")
    assert jsonData["status"] == "error"
    
    assert len(jsonData["message"]) > 0, "Message field should not be empty"
    logger.info(f"Error message: \"{jsonData['message']}\"")
    
    logger.info(f"Validating against ERROR_SCHEMA")
    from schemas.auth_schema import ERROR_SCHEMA
    assert_schema(jsonData, ERROR_SCHEMA)
    
    return jsonData

  
def assert_no_server_error(response):
    logger.info(f"Checking that server did not crash")
    assert response.status_code != 500, (
        f"Server returned 500 internal server error\n Request Body: {response.text}"
    )
    logger.info(f"Server is okay -- ({response.status_code})")
    


