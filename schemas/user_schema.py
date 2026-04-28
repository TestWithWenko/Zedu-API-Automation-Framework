USER_PROFILE_SCHEMA = {
    "type": "object",
    "required": ["status", "status_code", "message", "data"],
    "properties": {
        "status":      {"type": "string"},
        "status_code": {"type": "integer"},
        "message":     {"type": "string"},
        "data": {
            "type": "object",
            "required": ["id", "email", "profile"],
            "properties": {
                "id":        {"type": "string"},
                "email":     {"type": "string"},
                "profile": {"type": "object"},
            },
            "additionalProperties": True
        }
    }
}

USER_UPDATE_SCHEMA = {
    "type": "object",
    "required": ["status", "status_code", "message", "profile"],
    "properties": {
        "status":      {"type": "string"},
        "status_code": {"type": "integer"},
        "message":     {"type": "string"},
        "profile": {
            "type": "object",
            "required": ["first_name", "last_name", "phone", "user_id"],
            "properties": {
                "first_name": {"type": "string"},
                "last_name":  {"type": "string"},
                "phone":     {"type": "string"},
                "user_id":  {"type": "string"},
            },
            "additionalProperties": True
        }
    }
}