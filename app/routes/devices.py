from flask import Blueprint, jsonify, render_template, current_app

from app.services import device_service

devices_bp = Blueprint("devices", __name__)


@devices_bp.route("/devices")
def devices_page():
    return render_template("devices.html", active_page="devices")


@devices_bp.route("/api/devices")
def api_devices():
    offline_threshold = current_app.config["DEVICE_OFFLINE_THRESHOLD_SECONDS"]
    return jsonify(device_service.list_devices(offline_threshold))


@devices_bp.route("/api/devices/<device_id>")
def api_device_detail(device_id):
    offline_threshold = current_app.config["DEVICE_OFFLINE_THRESHOLD_SECONDS"]
    device = device_service.get_device(device_id, offline_threshold)
    if device is None:
        return jsonify({"success": False, "message": "Device not found"}), 404
    return jsonify(device)
