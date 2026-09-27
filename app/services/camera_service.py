"""Holds the most recent camera frame in memory so the live feed / MJPEG
stream and on-demand AI analysis always have something to read, without
writing every single frame to disk (PRD Section 46 — only persist selected
snapshots, analysed frames, and evaluation images).
"""
import threading
from datetime import datetime

_lock = threading.Lock()
_state = {
    "device_id": None,
    "jpeg_bytes": None,
    "received_at": None,
}


def set_latest_frame(device_id, jpeg_bytes):
    with _lock:
        _state["device_id"] = device_id
        _state["jpeg_bytes"] = jpeg_bytes
        _state["received_at"] = datetime.utcnow()


def get_latest_frame():
    with _lock:
        return dict(_state)


def has_frame():
    with _lock:
        return _state["jpeg_bytes"] is not None
