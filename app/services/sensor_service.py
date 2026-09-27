from app.extensions import db
from app.models import SensorReading, Threshold
from app.services import alert_service
from app.utils.time_utils import resolve_range

PARAMETERS = ("temperature", "ph", "dissolved_oxygen", "turbidity")


def store_reading(cleaned_payload):
    reading = SensorReading(
        device_id=cleaned_payload["device_id"],
        temperature=cleaned_payload.get("temperature"),
        ph=cleaned_payload.get("ph"),
        dissolved_oxygen=cleaned_payload.get("dissolved_oxygen"),
        turbidity=cleaned_payload.get("turbidity"),
    )
    db.session.add(reading)
    db.session.commit()

    thresholds = {t.parameter: t for t in Threshold.query.all()}
    for parameter in PARAMETERS:
        value = cleaned_payload.get(parameter)
        if value is not None:
            alert_service.check_water_quality(parameter, value, thresholds.get(parameter))

    return reading


def latest_reading():
    return SensorReading.query.order_by(SensorReading.recorded_at.desc()).first()


def current_status():
    """Returns the latest value + status per parameter for dashboard cards."""
    reading = latest_reading()
    thresholds = {t.parameter: t for t in Threshold.query.all()}

    result = {}
    for parameter in PARAMETERS:
        threshold = thresholds.get(parameter)
        value = getattr(reading, parameter) if reading else None
        result[parameter] = {
            "value": value,
            "status": threshold.status_for(value) if threshold else ("Unknown" if value is None else "Normal"),
            "last_updated": reading.recorded_at.isoformat() if reading else None,
        }
    return result


def history(period="24h", device_id=None, start=None, end=None):
    start_dt, end_dt = resolve_range(period, start, end)
    query = SensorReading.query.filter(
        SensorReading.recorded_at >= start_dt, SensorReading.recorded_at <= end_dt
    )
    if device_id:
        query = query.filter_by(device_id=device_id)
    readings = query.order_by(SensorReading.recorded_at.asc()).all()
    return [r.to_dict() for r in readings]
