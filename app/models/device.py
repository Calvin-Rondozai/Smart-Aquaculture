from datetime import datetime, timedelta

from app.extensions import db


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    device_type = db.Column(db.String(64), nullable=False)  # e.g. "ESP32 Sensor Node", "ESP32-CAM"
    ip_address = db.Column(db.String(64), nullable=True)
    firmware_version = db.Column(db.String(32), nullable=True)
    last_seen = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def status(self, offline_threshold_seconds=120):
        if self.last_seen is None:
            return "Unknown"
        if datetime.utcnow() - self.last_seen > timedelta(seconds=offline_threshold_seconds):
            return "Offline"
        return "Online"

    def touch(self, ip_address=None, firmware_version=None):
        self.last_seen = datetime.utcnow()
        if ip_address:
            self.ip_address = ip_address
        if firmware_version:
            self.firmware_version = firmware_version

    def to_dict(self, offline_threshold_seconds=120):
        return {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type,
            "ip_address": self.ip_address,
            "firmware_version": self.firmware_version,
            "status": self.status(offline_threshold_seconds),
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat(),
        }
