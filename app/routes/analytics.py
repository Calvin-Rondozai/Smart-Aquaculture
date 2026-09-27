from flask import Blueprint, current_app, jsonify, render_template, request

from app.models import Alert, FishDetection
from app.services import device_service
from app.utils.time_utils import resolve_range

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
def analytics_page():
    return render_template("analytics.html", active_page="analytics")


@analytics_bp.route("/api/analytics")
def api_analytics():
    period = request.args.get("period", "24h")
    start_dt, end_dt = resolve_range(period, request.args.get("start"), request.args.get("end"))

    detections = (
        FishDetection.query.filter(FishDetection.created_at >= start_dt, FishDetection.created_at <= end_dt)
        .order_by(FishDetection.created_at.asc())
        .all()
    )

    fish_trend = [{"timestamp": d.created_at.isoformat(), "fish_count": d.fish_count} for d in detections]
    biomass_trend = [
        {
            "timestamp": d.created_at.isoformat(),
            "estimated_biomass": d.biomass_estimate.estimated_biomass if d.biomass_estimate else None,
        }
        for d in detections
    ]

    inference_times = [d.inference_time_ms for d in detections if d.inference_time_ms is not None]
    confidences = [d.average_confidence for d in detections if d.average_confidence is not None]
    avg_inference_ms = round(sum(inference_times) / len(inference_times), 1) if inference_times else None

    ai_performance = {
        "average_inference_time_ms": avg_inference_ms,
        "fps": round(1000 / avg_inference_ms, 2) if avg_inference_ms else None,
        "average_confidence": round(sum(confidences) / len(confidences), 3) if confidences else None,
        "analyses_count": len(detections),
        # Ground-truth evaluation metrics require a labeled test set, which
        # has not been run yet — reported honestly rather than fabricated.
        "precision": None,
        "recall": None,
        "f1_score": None,
        "map_50": None,
        "map_50_95": None,
        "counting_error": None,
        "evaluation_status": "Not yet evaluated",
    }

    offline_threshold = current_app.config["DEVICE_OFFLINE_THRESHOLD_SECONDS"]
    devices = device_service.list_devices(offline_threshold)
    device_uptime = {
        "devices_total": len(devices),
        "devices_online": sum(1 for d in devices if d["status"] == "Online"),
    }

    alerts_in_period = Alert.query.filter(
        Alert.created_at >= start_dt, Alert.created_at <= end_dt
    ).count()

    return jsonify(
        {
            "period": period,
            "fish_count_trend": fish_trend,
            "biomass_trend": biomass_trend,
            "ai_performance": ai_performance,
            "device_uptime": device_uptime,
            "alert_count": alerts_in_period,
            "analysis_count": len(detections),
        }
    )
