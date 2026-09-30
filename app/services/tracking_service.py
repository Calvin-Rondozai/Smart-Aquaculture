"""Multi-object tracking for detected fish across consecutive analysed
frames, using the `trackers` package's ByteTrackTracker (a real Kalman
filter based multi-object tracker), instead of a hand-rolled heuristic.

Detection alone re-identifies nothing between frames — the same fish
swimming past the camera would otherwise be counted again on every
analysis, inflating any trend or population estimate built on raw counts.
This assigns a persistent `track_id` to each detection, which is the
basis for a real "unique individuals seen" population estimate (PRD
Section 15) instead of a naive average of per-frame counts.

Why `trackers.ByteTrackTracker` rather than `supervision.ByteTrack`: the
copy bundled in `supervision` is deprecated (removed as of v0.31.0) in
favour of this dedicated package, per supervision's own docs. `trackers`
is passed real wall-clock timestamps per update (not an assumed fixed
frame rate), so its Kalman motion model correctly accounts for the
actual (often multi-second, CPU-inference-bound) gap between analyses
rather than assuming 30fps video.

Works identically regardless of which detector backend produced the
boxes (stub, CFD, or the tilapia pose model), since tracking only needs
bounding boxes + confidence.
"""
import threading
import time

import numpy as np
import supervision as sv
from trackers import ByteTrackTracker


class FishTracker:
    def __init__(
        self,
        track_activation_threshold=0.25,
        # `lost_track_buffer` is internally divided by a hardcoded 30 to get
        # a real-seconds timeout, regardless of `frame_rate` — i.e. the
        # default (30) means a track is dropped after just ONE real second
        # without a match. Our analyses land anywhere from ~0.7s (OpenVINO
        # GPU) to several seconds apart (CPU fallback), so 450 (~15s) is
        # the actual real-world tolerance we need; do not "simplify" this
        # back toward the library's default without re-reading that math.
        lost_track_buffer=450,
        minimum_consecutive_frames=1,
        minimum_iou_threshold=0.1,
    ):
        self._lock = threading.Lock()
        self._track_activation_threshold = track_activation_threshold
        self._lost_track_buffer = lost_track_buffer
        self._minimum_consecutive_frames = minimum_consecutive_frames
        self._minimum_iou_threshold = minimum_iou_threshold
        self._tracker = self._new_tracker()

    def _new_tracker(self):
        return ByteTrackTracker(
            track_activation_threshold=self._track_activation_threshold,
            lost_track_buffer=self._lost_track_buffer,
            minimum_consecutive_frames=self._minimum_consecutive_frames,
            minimum_iou_threshold=self._minimum_iou_threshold,
        )

    def init_app(self, app):
        """Aligns the tracker's activation threshold with the detector's
        confidence threshold — a detection the detector itself considers
        too weak to count shouldn't be spawning/confirming tracks either."""
        self._track_activation_threshold = app.config["FISH_DETECTION_CONFIDENCE_THRESHOLD"]
        self._tracker = self._new_tracker()

    def reset(self):
        with self._lock:
            self._tracker = self._new_tracker()

    def update(self, detections):
        """Matches `detections` (list of dicts with x1/y1/x2/y2/confidence)
        against existing tracks and returns the same list with a
        `track_id` key added to each detection (None if the track hasn't
        been confirmed yet — ByteTrack's first sighting of a new object
        is tentative by design)."""
        with self._lock:
            if not detections:
                # Still advance the tracker's internal clock/aging even on
                # an empty frame, so lost tracks age out correctly.
                empty = sv.Detections.empty()
                self._tracker.update(empty, timestamp=time.time())
                return []

            xyxy = np.array(
                [[d["x1"], d["y1"], d["x2"], d["y2"]] for d in detections], dtype=np.float32
            )
            confidence = np.array([d["confidence"] for d in detections], dtype=np.float32)
            class_id = np.zeros(len(detections), dtype=int)
            # Keypoints (from a pose-capable detector) aren't part of the
            # box geometry ByteTrack matches on, but ride along per-index
            # via `data` so they survive the update and can be reattached.
            has_keypoints = any("keypoints" in d for d in detections)
            data = (
                {"keypoints": [d.get("keypoints") for d in detections]} if has_keypoints else {}
            )

            sv_detections = sv.Detections(
                xyxy=xyxy, confidence=confidence, class_id=class_id, data=data
            )
            tracked = self._tracker.update(sv_detections, timestamp=time.time())

            results = []
            for i in range(len(tracked)):
                x1, y1, x2, y2 = [float(v) for v in tracked.xyxy[i]]
                raw_id = int(tracked.tracker_id[i]) if tracked.tracker_id is not None else -1
                detection = {
                    "class": "fish",
                    "confidence": round(float(tracked.confidence[i]), 3),
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "track_id": raw_id if raw_id >= 0 else None,
                }
                if has_keypoints:
                    detection["keypoints"] = tracked.data["keypoints"][i]
                results.append(detection)
            return results


fish_tracker = FishTracker()
