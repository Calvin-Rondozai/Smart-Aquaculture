import os

import cv2
import numpy as np


def decode_image_bytes(image_bytes):
    """Decodes raw image bytes (JPEG/PNG) into a BGR numpy array, or None
    if the bytes are not a valid image."""
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return image


def save_image(image_bgr, directory, filename):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    cv2.imwrite(path, image_bgr)
    return path


def draw_detections(image_bgr, detections, color=(246, 130, 59)):
    """Draws thin single-colour bounding boxes with small confidence labels,
    matching the PRD's restrained overlay style (Section 12). Colour is BGR;
    default is the primary blue (#3B82F6) in BGR order.
    """
    annotated = image_bgr.copy()
    for d in detections:
        x1, y1, x2, y2 = int(d["x1"]), int(d["y1"]), int(d["x2"]), int(d["y2"])
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 1)
        for kx, ky in d.get("keypoints") or []:
            cv2.circle(annotated, (int(kx), int(ky)), 3, color, -1)
        label = f"#{d['track_id']} {d['confidence']:.0%}" if d.get("track_id") is not None else f"{d['confidence']:.0%}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        cv2.rectangle(annotated, (x1, max(0, y1 - th - 6)), (x1 + tw + 6, y1), color, -1)
        cv2.putText(
            annotated, label, (x1 + 3, max(12, y1 - 4)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA,
        )
    return annotated


def encode_image_to_jpeg(image_bgr, quality=85):
    success, buffer = cv2.imencode(".jpg", image_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not success:
        return None
    return buffer.tobytes()
