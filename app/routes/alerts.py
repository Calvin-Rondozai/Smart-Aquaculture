from flask import Blueprint, jsonify, render_template, request

from app.models import Alert
from app.services import alert_service

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/alerts")
def alerts_page():
    return render_template("alerts.html", active_page="alerts")


@alerts_bp.route("/api/alerts")
def api_alerts():
    resolved_param = request.args.get("resolved")
    query = Alert.query
    if resolved_param is not None:
        query = query.filter_by(resolved=resolved_param.lower() == "true")
    alerts = query.order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])


@alerts_bp.route("/api/alerts/<int:alert_id>/resolve", methods=["POST"])
def api_resolve_alert(alert_id):
    alert = alert_service.resolve_alert(alert_id)
    if alert is None:
        return jsonify({"success": False, "message": "Alert not found"}), 404
    return jsonify({"success": True, "alert": alert.to_dict()})
