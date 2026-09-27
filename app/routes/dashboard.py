from datetime import datetime

from flask import Blueprint, jsonify, render_template, current_app

from app.models import Alert, FishDetection
from app.services import sensor_service, device_service

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template("dashboard.html", active_page="dashboard")


@dashboard_bp.route("/api/dashboard")
def api_dashboard():
    offline_threshold = current_app.config["DEVICE_OFFLINE_THRESHOLD_SECONDS"]
    devices = device_service.list_devices(offline_threshold)
    any_online = any(d["status"] == "Online" for d in devices)

    water_quality = sensor_service.current_status()

    latest_detection = FishDetection.query.order_by(FishDetection.created_at.desc()).first()
    fish = None
    biomass = None
    if latest_detection:
        fish = {
            "fish_count": latest_detection.fish_count,
            "average_confidence": latest_detection.average_confidence,
            "last_updated": latest_detection.created_at.isoformat(),
        }
        if latest_detection.biomass_estimate:
            biomass = latest_detection.biomass_estimate.to_dict()

    open_alerts = Alert.query.filter_by(resolved=False).order_by(Alert.created_at.desc()).limit(5).all()

    return jsonify(
        {
            "system_status": "Online" if any_online else "Offline",
            "server_time": datetime.utcnow().isoformat(),
            "water_quality": water_quality,
            "fish": fish,
            "biomass": biomass,
            "recent_alerts": [a.to_dict() for a in open_alerts],
            "devices_online": sum(1 for d in devices if d["status"] == "Online"),
            "devices_total": len(devices),
        }
    )
