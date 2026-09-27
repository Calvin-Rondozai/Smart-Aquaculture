from datetime import datetime

from app.extensions import db


class CameraFrame(db.Model):
    __tablename__ = "camera_frames"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), db.ForeignKey("devices.device_id"), nullable=False, index=True)
    image_path = db.Column(db.String(256), nullable=False)
    captured_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed = db.Column(db.Boolean, default=False, nullable=False)

    detections = db.relationship("FishDetection", backref="frame", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "image_path": self.image_path,
            "captured_at": self.captured_at.isoformat(),
            "processed": self.processed,
        }
