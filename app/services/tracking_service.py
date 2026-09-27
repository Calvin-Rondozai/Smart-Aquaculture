"""Multi-object tracking for detected fish across consecutive analysed
frames.

Detection alone re-identifies nothing between frames — the same fish
swimming past the camera would otherwise be counted again on every
analysis, inflating any trend or population estimate built on raw counts.
This assigns a persistent `track_id` to each detection using greedy IoU
matching against the previous frames' tracks (a minimal SORT-style
tracker, no Kalman filter/motion model — adequate for the ~3s analysis
cadence used here, since real fish don't move far frame-to-frame at that
rate). Track IDs are then the basis for a real "unique individuals seen"
population estimate (PRD Section 15) instead of a naive average of
per-frame counts.

Works identically regardless of which detector backend produced the
boxes (stub or CFD), since tracking only needs bounding boxes.
"""
import threading


def _iou(a, b):
    x1 = max(a["x1"], b["x1"])
    y1 = max(a["y1"], b["y1"])
    x2 = min(a["x2"], b["x2"])
    y2 = min(a["y2"], b["y2"])

    inter_w = max(0.0, x2 - x1)
    inter_h = max(0.0, y2 - y1)
    intersection = inter_w * inter_h
    if intersection <= 0:
        return 0.0

    area_a = max(0.0, a["x2"] - a["x1"]) * max(0.0, a["y2"] - a["y1"])
    area_b = max(0.0, b["x2"] - b["x1"]) * max(0.0, b["y2"] - b["y1"])
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0


class FishTracker:
    def __init__(self, iou_threshold=0.3, max_age=3):
        self._lock = threading.Lock()
        self._iou_threshold = iou_threshold
        self._max_age = max_age  # consecutive missed frames before a track is dropped
        self._next_id = 1
        self._tracks = {}  # track_id -> {"bbox": {...}, "age": int}

    def reset(self):
        with self._lock:
            self._next_id = 1
            self._tracks = {}

    def update(self, detections):
        """Matches `detections` (list of dicts with x1/y1/x2/y2/confidence)
        against existing tracks and returns the same list with a
        `track_id` key added to each detection."""
        with self._lock:
            unmatched_track_ids = set(self._tracks.keys())
            results = []

            for detection in detections:
                best_track_id = None
                best_iou = self._iou_threshold

                for track_id in unmatched_track_ids:
                    score = _iou(detection, self._tracks[track_id]["bbox"])
                    if score > best_iou:
                        best_iou = score
                        best_track_id = track_id

                if best_track_id is not None:
                    unmatched_track_ids.discard(best_track_id)
                    self._tracks[best_track_id] = {"bbox": detection, "age": 0}
                    track_id = best_track_id
                else:
                    track_id = self._next_id
                    self._next_id += 1
                    self._tracks[track_id] = {"bbox": detection, "age": 0}

                results.append({**detection, "track_id": track_id})

            # Age out tracks that had no match this frame; drop once stale.
            for track_id in unmatched_track_ids:
                self._tracks[track_id]["age"] += 1
            self._tracks = {
                tid: t for tid, t in self._tracks.items() if t["age"] <= self._max_age
            }

            return results


fish_tracker = FishTracker()
