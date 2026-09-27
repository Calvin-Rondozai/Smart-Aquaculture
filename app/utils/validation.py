ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png"}
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}

# Sane physical bounds for pond sensors — requests outside these ranges are
# rejected rather than silently stored (PRD Section 28).
SENSOR_RANGES = {
    "temperature": (0, 45),       # deg C
    "ph": (0, 14),
    "dissolved_oxygen": (0, 20),  # mg/L
    "turbidity": (0, 1000),       # NTU
}


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def require_fields(payload, fields):
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object")
    missing = [f for f in fields if f not in payload or payload[f] in (None, "")]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")


def validate_sensor_reading(payload):
    require_fields(payload, ["device_id"])

    cleaned = {"device_id": str(payload["device_id"])}
    for field, (low, high) in SENSOR_RANGES.items():
        if field not in payload or payload[field] is None:
            cleaned[field] = None
            continue
        try:
            value = float(payload[field])
        except (TypeError, ValueError):
            raise ValidationError(f"Field '{field}' must be a number")
        if not (low <= value <= high):
            raise ValidationError(f"Field '{field}' value {value} out of valid range [{low}, {high}]")
        cleaned[field] = value

    return cleaned


def secure_image_filename(device_id, extension):
    safe_device_id = "".join(c for c in device_id if c.isalnum() or c in ("-", "_")) or "device"
    from datetime import datetime

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")
    return f"{safe_device_id}_{timestamp}.{extension}"
