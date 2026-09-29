"""Multi-object tracking for detected fish across consecutive analysed
frames.

Detection alone re-identifies nothing between frames — the same fish
swimming past the camera would otherwise be counted again on every
analysis, inflating any trend or population estimate built on raw counts.
This assigns a persistent `track_id` to each detection by matching
against the previous analyses' tracks. Track IDs are then the basis for
a real "unique individuals seen" population estimate (PRD Section 15)
instead of a naive average of per-frame counts.

Matching is by normalized centroid distance, not IoU. IoU degrades to
zero very quickly once a box moves by roughly its own size — fine for
30fps video, but analyses here are seconds apart (CPU inference on a
large model), so a fish can easily move further than its own body
length between two consecutive analyses despite being the same fish.
Distance is normalized by the boxes' own size, so a fast-moving large
fish and a slow-moving small fish are judged on the same relative scale
rather than a fixed pixel radius.

Works identically regardless of which detector backend produced the
boxes (stub or CFD), since tracking only needs bounding boxes.
"""
import math
import threading


def _centroid(box):
    return ((box["x1"] + box["x2"]) / 2.0, (box["y1"] + box["y2"]) / 2.0)


def _diagonal(box):
    return math.hypot(box["x2"] - box["x1"], box["y2"] - box["y1"])


def _normalized_distance(a, b):
    """Centroid distance divided by the average box diagonal — a value
    around 1.0 means the centers moved about one fish-length apart."""
    ax, ay = _centroid(a)
    bx, by = _centroid(b)
    distance = math.hypot(ax - bx, ay - by)
    scale = max(1.0, (_diagonal(a) + _diagonal(b)) / 2.0)
    return distance / scale


class FishTracker:
    def __init__(self, max_normalized_distance=2.5, max_age=6):
        self._lock = threading.Lock()
        # How many fish-lengths a centroid may move between analyses and
        # still be considered the same fish. Generous on purpose: at a
        # multi-second analysis cadence a fish can easily cross this much
        # of the frame, and a missed continuation (new ID) hurts the
        # "track it as it moves" goal more than an occasional wrong match.
        self._max_normalized_distance = max_normalized_distance
        self._max_age = max_age  # consecutive missed analyses before a track is dropped
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

            # Greedy nearest-neighbour: process closest pairs first so one
            # detection can't steal another's better match.
            candidates = []
            for i, detection in enumerate(detections):
                for track_id in unmatched_track_ids:
                    dist = _normalized_distance(detection, self._tracks[track_id]["bbox"])
                    if dist <= self._max_normalized_distance:
                        candidates.append((dist, i, track_id))
            candidates.sort(key=lambda c: c[0])

            assigned_track_id = {}
            claimed_tracks = set()
            for dist, i, track_id in candidates:
                if i in assigned_track_id or track_id in claimed_tracks:
                    continue
                assigned_track_id[i] = track_id
                claimed_tracks.add(track_id)

            for i, detection in enumerate(detections):
                track_id = assigned_track_id.get(i)
                if track_id is not None:
                    unmatched_track_ids.discard(track_id)
                else:
                    track_id = self._next_id
                    self._next_id += 1

                self._tracks[track_id] = {"bbox": detection, "age": 0}
                results.append({**detection, "track_id": track_id})

            # Age out tracks that had no match this analysis; drop once stale.
            for track_id in unmatched_track_ids:
                self._tracks[track_id]["age"] += 1
            self._tracks = {
                tid: t for tid, t in self._tracks.items() if t["age"] <= self._max_age
            }

            return results


fish_tracker = FishTracker()
