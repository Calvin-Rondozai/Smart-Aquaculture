"""Biomass estimation service.

Pipeline: Fish detection -> Fish size estimation (pixels -> cm, requires a
camera calibration factor) -> Weight estimation (allometric length-weight
relationship) -> Individual biomass -> Total biomass.

Without a calibration factor (pixels-per-cm for the deployed camera/pond
setup) there is no reliable way to turn a bounding box into a real-world
length, so this service returns "unavailable" rather than inventing a
number (PRD Section 16, Non-Negotiable Rule 7).
"""
import math

# Set via Settings once a camera is calibrated against a known reference
# object at the pond. None => biomass estimation is reported unavailable.
PIXELS_PER_CM = None

# Generic allometric length-weight coefficients (W = a * L^b, W in grams,
# L in cm). These are placeholder generic-fish constants; replace with
# species-specific coefficients once known for the farmed species.
ALLOMETRIC_A = 0.0125
ALLOMETRIC_B = 3.0


def _bbox_length_cm(detection, pixels_per_cm):
    diagonal_px = math.hypot(
        detection["x2"] - detection["x1"], detection["y2"] - detection["y1"]
    )
    return diagonal_px / pixels_per_cm


def _weight_grams(length_cm):
    return ALLOMETRIC_A * (length_cm ** ALLOMETRIC_B)


def estimate_biomass(detections, pixels_per_cm=PIXELS_PER_CM):
    """Returns a dict describing the biomass estimate, or an 'unavailable'
    result if calibration data is missing or there are no detections."""
    if not detections:
        return {
            "estimated_biomass": None,
            "method": "unavailable",
            "confidence": None,
            "status": "unavailable",
        }

    if not pixels_per_cm:
        return {
            "estimated_biomass": None,
            "method": "unavailable_no_calibration",
            "confidence": None,
            "status": "unavailable",
        }

    total_grams = 0.0
    for detection in detections:
        length_cm = _bbox_length_cm(detection, pixels_per_cm)
        total_grams += _weight_grams(length_cm)

    avg_confidence = round(sum(d["confidence"] for d in detections) / len(detections), 3)

    return {
        "estimated_biomass": round(total_grams / 1000.0, 3),  # kg
        "method": "allometric_length_weight",
        "confidence": avg_confidence,
        "status": "estimated",
    }
