import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _resolve_database_uri():
    """Relative sqlite URIs are resolved against BASE_DIR (not the process's
    current working directory, which varies by how the app is launched)."""
    raw = os.environ.get("DATABASE_URL", "sqlite:///instance/aquaculture.db")
    prefix = "sqlite:///"
    if raw.startswith(prefix) and not raw[len(prefix):].startswith("/"):
        relative_path = raw[len(prefix):]
        if not os.path.isabs(relative_path):
            absolute_path = os.path.join(BASE_DIR, relative_path)
            return prefix + absolute_path.replace("\\", "/")
    return raw


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ESP32_API_KEY = os.environ.get("ESP32_API_KEY", "change-me")

    FISH_DETECTION_MODEL_PATH = os.environ.get(
        "FISH_DETECTION_MODEL_PATH", "models/fish_detection/cfd-yolov12x-1.00.pt"
    )
    FISH_DETECTION_CONFIDENCE_THRESHOLD = float(
        os.environ.get("FISH_DETECTION_CONFIDENCE_THRESHOLD", "0.25")
    )
    FISH_DETECTION_BACKEND = os.environ.get("FISH_DETECTION_BACKEND", "stub")
    # Unverified/unlicensed prototype option — see TilapiaPoseDetector's
    # docstring before using this outside local evaluation.
    TILAPIA_MODEL_PATH = os.environ.get(
        "TILAPIA_MODEL_PATH", "models/fish_detection/tilapia-pose-yolov8n.pt"
    )
    # 1024 = the model's native training resolution (best recall). The "x"
    # model variant is slow on CPU-only hardware (Section 48: avoid blocking
    # Flask requests with long inference calls) — drop this if you need
    # faster updates more than maximum recall, or raise imgsz further only
    # if you have a GPU.
    FISH_DETECTION_IMGSZ = int(os.environ.get("FISH_DETECTION_IMGSZ", "1024"))

    CAMERA_FRAME_INTERVAL = int(os.environ.get("CAMERA_FRAME_INTERVAL", "5"))
    MAX_IMAGE_UPLOAD_MB = int(os.environ.get("MAX_IMAGE_UPLOAD_MB", "8"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_IMAGE_UPLOAD_MB", "8")) * 1024 * 1024

    STORAGE_DIR = os.path.join(BASE_DIR, "storage")
    CAMERA_STORAGE_DIR = os.path.join(STORAGE_DIR, "camera")
    PROCESSED_STORAGE_DIR = os.path.join(STORAGE_DIR, "processed")
    EXPORTS_STORAGE_DIR = os.path.join(STORAGE_DIR, "exports")

    # Device is considered offline if no reading/frame seen within this many seconds.
    DEVICE_OFFLINE_THRESHOLD_SECONDS = int(os.environ.get("DEVICE_OFFLINE_THRESHOLD_SECONDS", "120"))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
