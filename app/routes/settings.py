from flask import Blueprint, current_app, jsonify, render_template, request

from app.extensions import db
from app.models import Threshold
from app.services.fish_detection_service import fish_detection_service

settings_bp = Blueprint("settings", __name__)

APP_VERSION = "0.1.0-dev"


@settings_bp.route("/settings")
def settings_page():
    return render_template(
        "settings.html",
        active_page="settings",
        model_info=fish_detection_service.model_info(),
        app_version=APP_VERSION,
    )


@settings_bp.route("/api/settings/config")
def api_config():
    return jsonify(
        {
            "camera_frame_interval_seconds": current_app.config["CAMERA_FRAME_INTERVAL"],
            "fish_detection_confidence_threshold": current_app.config["FISH_DETECTION_CONFIDENCE_THRESHOLD"],
            "device_offline_threshold_seconds": current_app.config["DEVICE_OFFLINE_THRESHOLD_SECONDS"],
        }
    )


@settings_bp.route("/api/settings/thresholds")
def api_list_thresholds():
    thresholds = Threshold.query.order_by(Threshold.parameter.asc()).all()
    return jsonify([t.to_dict() for t in thresholds])


@settings_bp.route("/api/settings/thresholds/<parameter>", methods=["PUT"])
def api_update_threshold(parameter):
    threshold = Threshold.query.filter_by(parameter=parameter).first()
    if threshold is None:
        return jsonify({"success": False, "message": "Unknown parameter"}), 404

    payload = request.get_json(silent=True) or {}
    for field in ("minimum_value", "maximum_value", "warning_level", "critical_level"):
        if field in payload:
            value = payload[field]
            setattr(threshold, field, float(value) if value is not None else None)

    db.session.commit()
    return jsonify({"success": True, "threshold": threshold.to_dict()})


@settings_bp.route("/api/settings/about")
def api_about():
    return jsonify(
        {
            "app_version": APP_VERSION,
            "model_info": fish_detection_service.model_info(),
        }
    )
