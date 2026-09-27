from functools import wraps

from flask import current_app, jsonify, request


def require_device_api_key(view_func):
    """Guards ESP32 ingestion endpoints with a shared API key (PRD Section 31).
    Expected header: X-API-Key: <ESP32_API_KEY>
    """

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        expected = current_app.config["ESP32_API_KEY"]
        provided = request.headers.get("X-API-Key")
        if not expected or provided != expected:
            return jsonify({"success": False, "message": "Invalid or missing API key"}), 401
        return view_func(*args, **kwargs)

    return wrapped
