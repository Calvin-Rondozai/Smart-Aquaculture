import json
import time

from flask import Blueprint, Response, current_app, jsonify, render_template, request

from app.extensions import db
from app.models import BiomassEstimate, CameraFrame, DetectionObject, FishDetection
from app.services import alert_service, biomass_service, camera_service, device_service
from app.services.fish_detection_service import fish_detection_service
from app.services.tracking_service import fish_tracker
from app.utils.auth import require_device_api_key
from app.utils.image_utils import decode_image_bytes, draw_detections, encode_image_to_jpeg, save_image
from app.utils.time_utils import resolve_range
from app.utils.validation import secure_image_filename

camera_bp = Blueprint("camera", __name__)

WEBCAM_DEVICE_ID = "webcam-01"
LOW_CONFIDENCE_ALERT_THRESHOLD = 0.60
STREAM_FRAME_INTERVAL_SECONDS = 0.2


@camera_bp.route("/camera-ai")
def camera_ai_page():
    return render_template(
        "camera_ai.html",
        active_page="camera-ai",
        model_info=fish_detection_service.model_info(),
    )


def _ingest_frame(device_id, image_bytes):
    image = decode_image_bytes(image_bytes)
    if image is None:
        return None
    jpeg_bytes = encode_image_to_jpeg(image)
    camera_service.set_latest_frame(device_id, jpeg_bytes)
    return image


@camera_bp.route("/api/camera/frame", methods=["POST"])
@require_device_api_key
def post_camera_frame():
    device_id = request.form.get("device_id") or request.args.get("device_id")
    if not device_id:
        return jsonify({"success": False, "message": "Missing device_id"}), 400

    image_file = request.files.get("image")
    image_bytes = image_file.read() if image_file else request.data
    if not image_bytes:
        return jsonify({"success": False, "message": "Missing image data"}), 400

    if _ingest_frame(device_id, image_bytes) is None:
        return jsonify({"success": False, "message": "Invalid image data"}), 400

    device = device_service.get_or_create_device(device_id, device_type="ESP32-CAM")
    alert_service.check_device_status(device)

    return jsonify({"success": True, "message": "Frame received"})


@camera_bp.route("/api/camera/webcam-frame", methods=["POST"])
def post_webcam_frame():
    """Browser-side ingestion for a PC webcam feed, standing in for the
    ESP32-CAM until real hardware is available. Uses the same in-memory
    frame buffer and the same downstream AI pipeline as /api/camera/frame,
    so nothing else changes when the ESP32-CAM is swapped in later."""
    image_file = request.files.get("image")
    image_bytes = image_file.read() if image_file else request.data
    if not image_bytes:
        return jsonify({"success": False, "message": "Missing image data"}), 400

    if _ingest_frame(WEBCAM_DEVICE_ID, image_bytes) is None:
        return jsonify({"success": False, "message": "Invalid image data"}), 400

    device = device_service.get_or_create_device(WEBCAM_DEVICE_ID, device_type="PC Webcam")
    alert_service.check_device_status(device)

    return jsonify({"success": True, "message": "Frame received"})


@camera_bp.route("/api/camera/latest")
def get_camera_latest():
    state = camera_service.get_latest_frame()
    if not state["jpeg_bytes"]:
        return jsonify({"success": False, "message": "No camera frame available yet"}), 404
    return Response(state["jpeg_bytes"], mimetype="image/jpeg")


@camera_bp.route("/api/camera/status")
def get_camera_status():
    state = camera_service.get_latest_frame()
    return jsonify(
        {
            "device_id": state["device_id"],
            "has_frame": state["jpeg_bytes"] is not None,
            "received_at": state["received_at"].isoformat() if state["received_at"] else None,
        }
    )


@camera_bp.route("/api/camera/stream")
def get_camera_stream():
    def generate():
        boundary = b"--frame"
        while True:
            state = camera_service.get_latest_frame()
            if state["jpeg_bytes"]:
                yield (
                    boundary + b"\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + state["jpeg_bytes"] + b"\r\n"
                )
            time.sleep(STREAM_FRAME_INTERVAL_SECONDS)

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


def _detection_to_response(detection: FishDetection):
    data = detection.to_dict()
    data["image_url"] = f"/media/processed/{detection.frame.image_path}"
    return data


@camera_bp.route("/api/ai/analyse", methods=["POST"])
def post_ai_analyse():
    if not camera_service.has_frame():
        return jsonify({"success": False, "message": "No camera frame available to analyse"}), 400

    state = camera_service.get_latest_frame()
    image = decode_image_bytes(state["jpeg_bytes"])

    try:
        result = fish_detection_service.analyse(image)
    except Exception as exc:  # model/inference failure — surface a clean alert, not a stack trace
        alert_service.create_alert(
            "ai_analysis_failure", "critical", f"Fish detection inference failed: {exc}"
        )
        return jsonify({"success": False, "message": "AI analysis failed"}), 500

    device_id = state["device_id"] or "unknown"
    tracked_detections = fish_tracker.update(result["detections"])

    annotated = draw_detections(image, tracked_detections)
    filename = secure_image_filename(device_id, "jpg")
    save_image(annotated, current_app.config["PROCESSED_STORAGE_DIR"], filename)

    frame = CameraFrame(device_id=device_id, image_path=filename, processed=True)
    db.session.add(frame)
    db.session.flush()

    detection = FishDetection(
        frame_id=frame.id,
        fish_count=result["fish_count"],
        average_confidence=result["average_confidence"],
        inference_time_ms=result["inference_time_ms"],
    )
    db.session.add(detection)
    db.session.flush()

    for det in tracked_detections:
        db.session.add(
            DetectionObject(
                detection_id=detection.id,
                class_name=det["class"],
                confidence=det["confidence"],
                x1=det["x1"],
                y1=det["y1"],
                x2=det["x2"],
                y2=det["y2"],
                track_id=det["track_id"],
                keypoints_json=json.dumps(det["keypoints"]) if det.get("keypoints") else None,
            )
        )

    biomass_result = biomass_service.estimate_biomass(result["detections"])
    db.session.add(
        BiomassEstimate(
            detection_id=detection.id,
            estimated_biomass=biomass_result["estimated_biomass"],
            method=biomass_result["method"],
            confidence=biomass_result["confidence"],
        )
    )

    db.session.commit()

    if result["average_confidence"] is not None and result["average_confidence"] < LOW_CONFIDENCE_ALERT_THRESHOLD:
        alert_service.create_alert(
            "low_detection_confidence",
            "warning",
            f"Average detection confidence ({result['average_confidence']:.0%}) is below {LOW_CONFIDENCE_ALERT_THRESHOLD:.0%}.",
        )

    response = _detection_to_response(detection)
    response["model_info"] = fish_detection_service.model_info()
    return jsonify(response)


@camera_bp.route("/api/ai/latest")
def get_ai_latest():
    detection = FishDetection.query.order_by(FishDetection.created_at.desc()).first()
    if detection is None:
        return jsonify({"success": False, "message": "No AI analyses yet"}), 404
    return jsonify(_detection_to_response(detection))


@camera_bp.route("/api/ai/history")
def get_ai_history():
    limit = min(int(request.args.get("limit", 50)), 200)
    detections = (
        FishDetection.query.order_by(FishDetection.created_at.desc()).limit(limit).all()
    )
    return jsonify([_detection_to_response(d) for d in detections])


@camera_bp.route("/api/fish/count")
def get_fish_count():
    latest = FishDetection.query.order_by(FishDetection.created_at.desc()).first()
    if latest is None:
        return jsonify({"detected_fish": None, "estimated_population": None, "status": "unavailable"})

    recent = FishDetection.query.order_by(FishDetection.created_at.desc()).limit(20).all()
    recent_ids = [d.id for d in recent]

    # Prefer counting distinct tracked individuals over the recent analysis
    # window — a fish seen in several consecutive frames is one fish, not
    # one-per-frame (PRD Section 15: population is derived from multiple
    # observations, not a single-frame count repeated).
    distinct_track_ids = (
        db.session.query(DetectionObject.track_id)
        .filter(DetectionObject.detection_id.in_(recent_ids), DetectionObject.track_id.isnot(None))
        .distinct()
        .count()
    )

    if distinct_track_ids:
        estimated_population = distinct_track_ids
        method = "unique_tracked_individuals_last_20_analyses"
    else:
        estimated_population = round(sum(d.fish_count for d in recent) / len(recent)) if recent else None
        method = "rolling_average_of_last_20_detections"

    return jsonify(
        {
            "detected_fish": latest.fish_count,
            "detected_fish_last_updated": latest.created_at.isoformat(),
            "estimated_population": estimated_population,
            "estimated_population_method": method,
        }
    )


@camera_bp.route("/api/fish/history")
def get_fish_history():
    period = request.args.get("period", "24h")
    start_dt, end_dt = resolve_range(period, request.args.get("start"), request.args.get("end"))
    detections = (
        FishDetection.query.filter(FishDetection.created_at >= start_dt, FishDetection.created_at <= end_dt)
        .order_by(FishDetection.created_at.asc())
        .all()
    )
    return jsonify(
        [{"timestamp": d.created_at.isoformat(), "fish_count": d.fish_count} for d in detections]
    )


@camera_bp.route("/api/biomass/latest")
def get_biomass_latest():
    detection = (
        FishDetection.query.join(BiomassEstimate)
        .order_by(FishDetection.created_at.desc())
        .first()
    )
    if detection is None or detection.biomass_estimate is None:
        return jsonify({"estimated_biomass": None, "status": "unavailable", "method": "unavailable"})
    return jsonify(detection.biomass_estimate.to_dict())


@camera_bp.route("/api/biomass/history")
def get_biomass_history():
    period = request.args.get("period", "24h")
    start_dt, end_dt = resolve_range(period, request.args.get("start"), request.args.get("end"))
    rows = (
        db.session.query(FishDetection, BiomassEstimate)
        .join(BiomassEstimate)
        .filter(FishDetection.created_at >= start_dt, FishDetection.created_at <= end_dt)
        .order_by(FishDetection.created_at.asc())
        .all()
    )
    return jsonify(
        [
            {
                "timestamp": detection.created_at.isoformat(),
                "estimated_biomass": biomass.estimated_biomass,
                "status": biomass.to_dict()["status"],
            }
            for detection, biomass in rows
        ]
    )
