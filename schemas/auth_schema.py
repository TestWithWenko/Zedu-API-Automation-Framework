# this is common to both login and registration, so its an helper to be used in both schemas
_USER_OBJECT_SCHEMA = {
    "type": "object",
    "required": [
        "id",
        "email",
        "first_name",
        "last_name",
        "fullname",
        "is_active",
        "is_onboarded",
        "is_verified",
    ],
    "properties": {
        "id":           {"type": "string"},
        "email":        {"type": "string"},
        "first_name":   {"type": "string"},
        "last_name":    {"type": "string"},
        "fullname":     {"type": "string"},
        "username":     {"type": "string"},
        "phone":        {"type": "string"},
        "avatar_url":   {"type": "string"},
        "is_active":    {"type": "boolean"},
        "is_onboarded": {"type": "boolean"},
        "is_verified":  {"type": "boolean"},
        "online":       {"type": "boolean"},
        "profile_updated": {"type": "boolean"},
        "created_at":   {"type": "string"},
        "updated_at":   {"type": "string"},
        "expires_in":   {"type": "string"},
        "user_id":      {"type": "string"},
    },
    "additionalProperties": True
}


REGISTER_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["status", "status_code", "message", "data"],
    "properties": {
        "status":      {"type": "string", "enum": ["success"]},
        "status_code": {"type": "integer", "enum": [201]},
        "message":     {"type": "string"},
        "data": {
            "type": "object",
            "required": ["access_token", "notification_token", "user"],
            "properties": {
                "access_token":       {"type": "string", "minLength": 10},
                "notification_token": {"type": "string", "minLength": 1},
                "user":               _USER_OBJECT_SCHEMA,
            },
            "additionalProperties": True
        }
    },
    "additionalProperties": False  
}

LOGIN_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["status", "status_code", "message", "data"],
    "properties": {
        "status":      {"type": "string", "enum": ["success"]},
        "status_code": {"type": "integer", "enum": [200]},
        "message":     {"type": "string"},
        "data": {
            "type": "object",
            "required": [
                "access_token",
                "access_token_expires_in",
                "notification_token",
                "user",
            ],
            "properties": {
                "access_token":             {"type": "string", "minLength": 10},
                "access_token_expires_in":  {"type": "string"},   # only in login
                "notification_token":       {"type": "string", "minLength": 1},
                "user":                     _USER_OBJECT_SCHEMA,
            },
            "additionalProperties": True
        }
    },
    "additionalProperties": False
}

LOGOUT_SUCCESS_SCHEMA = {
        "type": "object",
        "required": ["status", "status_code", "message"],
        "properties": {
        "status":      {"type": "string"},
        "status_code": {"type": "integer"},
        "message":     {"type": "string", "minLength": 1},
    }
}
        


ONBOARD_STATUS_SCHEMA = {
    "type": "object",
    "required": ["status", "status_code", "message", "data"],
    "properties": {
        "status":      {"type": "string", "enum": ["success"]},
        "status_code": {"type": "integer", "enum": [200]},
        "message":     {"type": "string"},
        "data": {
            "type": "object",
            "required": ["online", "status"],
            "properties": {
                "online": {"type": "boolean"},
                "status": {"type": "boolean"},   
            },
            "additionalProperties": False   
        }
    },
    "additionalProperties": False
}

ERROR_SCHEMA = {
    "type": "object",
    "required": ["status", "status_code", "message"],
    "properties": {
        "status":      {"type": "string", "enum": ["error"]},
        "status_code": {"type": "integer"},
        "message":     {"type": "string", "minLength": 1},
        "error": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                }
            ]
        }
    },
    "additionalProperties": False
}