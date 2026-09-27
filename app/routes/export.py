import csv
import io

from flask import Blueprint, Response, request

from app.models import FishDetection, SensorReading
from app.utils.time_utils import range_start_for

export_bp = Blueprint("export", __name__)


def _csv_response(filename, header, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@export_bp.route("/api/export/water-quality")
def export_water_quality():
    period = request.args.get("period", "30d")
    start = range_start_for(period)
    readings = (
        SensorReading.query.filter(SensorReading.recorded_at >= start)
        .order_by(SensorReading.recorded_at.asc())
        .all()
    )
    rows = [
        [r.recorded_at.isoformat(), r.device_id, r.temperature, r.ph, r.dissolved_oxygen, r.turbidity]
        for r in readings
    ]
    return _csv_response(
        "water_quality_export.csv",
        ["timestamp", "device_id", "temperature_c", "ph", "dissolved_oxygen_mgl", "turbidity_ntu"],
        rows,
    )


@export_bp.route("/api/export/fish-detections")
def export_fish_detections():
    period = request.args.get("period", "30d")
    start = range_start_for(period)
    detections = (
        FishDetection.query.filter(FishDetection.created_at >= start)
        .order_by(FishDetection.created_at.asc())
        .all()
    )
    rows = [
        [
            d.created_at.isoformat(),
            d.frame.device_id if d.frame else "",
            d.fish_count,
            d.average_confidence,
            d.inference_time_ms,
            d.biomass_estimate.estimated_biomass if d.biomass_estimate else "",
        ]
        for d in detections
    ]
    return _csv_response(
        "fish_detections_export.csv",
        ["timestamp", "device_id", "fish_count", "average_confidence", "inference_time_ms", "estimated_biomass_kg"],
        rows,
    )


@export_bp.route("/api/export/evaluation")
def export_evaluation():
    # No labeled evaluation dataset has been run yet — export the schema
    # with no rows rather than fabricating evaluation results.
    return _csv_response(
        "evaluation_export.csv",
        [
            "dataset", "model", "test_images", "correct_detections", "false_positives",
            "false_negatives", "precision", "recall", "f1_score", "map", "inference_time_ms",
        ],
        [],
    )
