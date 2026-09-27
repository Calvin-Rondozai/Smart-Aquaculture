from flask import Blueprint, jsonify, render_template, request

from app.models import Threshold
from app.services import sensor_service, device_service, alert_service
from app.utils.auth import require_device_api_key
from app.utils.validation import ValidationError, validate_sensor_reading

iot_bp = Blueprint("iot", __name__)


@iot_bp.route("/water-quality")
def water_quality_page():
    return render_template("water_quality.html", active_page="water-quality")


@iot_bp.route("/api/iot/readings", methods=["POST"])
@require_device_api_key
def post_reading():
    payload = request.get_json(silent=True) or {}
    try:
        cleaned = validate_sensor_reading(payload)
    except ValidationError as exc:
        return jsonify({"success": False, "message": exc.message}), 400

    device = device_service.get_or_create_device(cleaned["device_id"], device_type="ESP32 Sensor Node")
    alert_service.check_device_status(device)
    sensor_service.store_reading(cleaned)

    return jsonify({"success": True, "message": "Reading stored"})


@iot_bp.route("/api/water-quality/current")
def water_quality_current():
    return jsonify(sensor_service.current_status())


@iot_bp.route("/api/water-quality/history")
def water_quality_history():
    period = request.args.get("period", "24h")
    device_id = request.args.get("device_id")
    start = request.args.get("start")
    end = request.args.get("end")
    return jsonify(sensor_service.history(period=period, device_id=device_id, start=start, end=end))


@iot_bp.route("/api/water-quality/thresholds")
def water_quality_thresholds():
    thresholds = Threshold.query.all()
    return jsonify([t.to_dict() for t in thresholds])
