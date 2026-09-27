"""Fish detection service.

Isolates all model inference behind a single interface so the underlying
detector can be swapped (stub -> fine-tuned YOLO -> a future CFD release)
without touching routes, templates, or JS. Routes must never import a model
or run inference directly — only call FishDetectionService.
"""
import threading
import time

import cv2
import numpy as np


class BaseDetector:
    name = "unknown"
    version = "unknown"
    device = "CPU"

    def load(self):
        raise NotImplementedError

    def predict(self, image_bgr):
        """Return (detections, inference_time_ms). detections is a list of
        dicts: {class, confidence, x1, y1, x2, y2} in pixel coordinates."""
        raise NotImplementedError


class StubDetector(BaseDetector):
    """Development placeholder. Runs real OpenCV contour analysis (not
    fabricated numbers) so the full pipeline — counting, confidence display,
    bounding-box overlay, history — is exercised honestly before the real
    CFD model is wired in. Clearly labeled as a stub everywhere in the UI.
    """

    name = "Stub Contour Detector"
    version = "dev-0.1"
    device = "CPU"

    def load(self):
        return True

    def predict(self, image_bgr):
        start = time.time()
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 5
        )
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h, w = gray.shape[:2]
        frame_area = h * w
        min_area = frame_area * 0.0015
        max_area = frame_area * 0.25

        detections = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < min_area or area > max_area:
                continue
            x, y, bw, bh = cv2.boundingRect(c)
            aspect = bw / float(bh) if bh else 0
            if aspect < 0.3 or aspect > 3.5:
                continue
            perimeter = cv2.arcLength(c, True)
            circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter else 0
            confidence = float(np.clip(0.4 + circularity * 0.5, 0.4, 0.95))
            detections.append(
                {
                    "class": "fish",
                    "confidence": round(confidence, 3),
                    "x1": int(x),
                    "y1": int(y),
                    "x2": int(x + bw),
                    "y2": int(y + bh),
                }
            )

        inference_time_ms = (time.time() - start) * 1000
        return detections, inference_time_ms


class CFDDetector(BaseDetector):
    """Real detector: Community Fish Detector (YOLOv12x via ultralytics).
    Requires `pip install ultralytics torch` and downloaded weights at
    FISH_DETECTION_MODEL_PATH. See Section 13 of the PRD.
    """

    name = "Community Fish Detector (CFD)"
    version = "yolov12x-1.00"
    device = "CPU"

    def __init__(self, model_path, confidence_threshold, imgsz=640):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.imgsz = imgsz
        self._model = None

    def load(self):
        from ultralytics import YOLO  # imported lazily: heavy optional dependency

        self._model = YOLO(self.model_path)
        return True

    def predict(self, image_bgr):
        start = time.time()
        results = self._model.predict(source=image_bgr, imgsz=self.imgsz, device="cpu", verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                confidence = float(box.conf[0])
                if confidence < self.confidence_threshold:
                    continue
                x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                detections.append(
                    {
                        "class": "fish",
                        "confidence": round(confidence, 3),
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    }
                )
        inference_time_ms = (time.time() - start) * 1000
        return detections, inference_time_ms


class FishDetectionService:
    def __init__(self):
        self._detector = None
        self._confidence_threshold = 0.5
        self._loaded = False
        self._inference_lock = threading.Lock()  # serialize predict() calls — not safe under concurrent threads

    def init_app(self, app):
        self._confidence_threshold = app.config["FISH_DETECTION_CONFIDENCE_THRESHOLD"]
        backend = app.config["FISH_DETECTION_BACKEND"]

        if backend == "cfd":
            self._detector = CFDDetector(
                app.config["FISH_DETECTION_MODEL_PATH"],
                self._confidence_threshold,
                imgsz=app.config["FISH_DETECTION_IMGSZ"],
            )
        else:
            self._detector = StubDetector()

        self._detector.load()  # load once at startup — never per-request
        self._loaded = True

    @property
    def is_loaded(self):
        return self._loaded

    def model_info(self):
        return {
            "model": self._detector.name if self._detector else "Not loaded",
            "task": "Fish Detection",
            "status": "Loaded" if self._loaded else "Not loaded",
            "inference_device": self._detector.device if self._detector else "-",
            "model_version": self._detector.version if self._detector else "-",
            "is_stub": isinstance(self._detector, StubDetector),
        }

    def analyse(self, image_bgr):
        """Runs inference and returns a structured result. Confidence
        filtering happens here so `fish_count` only reflects detections
        above FISH_DETECTION_CONFIDENCE_THRESHOLD (PRD Section 14)."""
        if not self._loaded:
            raise RuntimeError("Fish detection model is not loaded")

        with self._inference_lock:
            all_detections, inference_time_ms = self._detector.predict(image_bgr)
        counted = [d for d in all_detections if d["confidence"] >= self._confidence_threshold]

        avg_confidence = (
            round(sum(d["confidence"] for d in counted) / len(counted), 3) if counted else None
        )

        return {
            "fish_count": len(counted),
            "detections": counted,
            "average_confidence": avg_confidence,
            "inference_time_ms": round(inference_time_ms, 1),
        }


fish_detection_service = FishDetectionService()
