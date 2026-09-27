from datetime import datetime

from app.extensions import db


class FishDetection(db.Model):
    __tablename__ = "fish_detections"

    id = db.Column(db.Integer, primary_key=True)
    frame_id = db.Column(db.Integer, db.ForeignKey("camera_frames.id"), nullable=False, index=True)
    fish_count = db.Column(db.Integer, nullable=False, default=0)
    average_confidence = db.Column(db.Float, nullable=True)
    inference_time_ms = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    objects = db.relationship("DetectionObject", backref="detection", lazy=True, cascade="all, delete-orphan")
    biomass_estimate = db.relationship(
        "BiomassEstimate", backref="detection", uselist=False, cascade="all, delete-orphan"
    )

    def to_dict(self, include_objects=True):
        data = {
            "id": self.id,
            "frame_id": self.frame_id,
            "fish_count": self.fish_count,
            "average_confidence": self.average_confidence,
            "inference_time_ms": self.inference_time_ms,
            "created_at": self.created_at.isoformat(),
        }
        if include_objects:
            data["detections"] = [o.to_dict() for o in self.objects]
        if self.biomass_estimate:
            data["biomass"] = self.biomass_estimate.to_dict()
        return data


class DetectionObject(db.Model):
    __tablename__ = "detection_objects"

    id = db.Column(db.Integer, primary_key=True)
    detection_id = db.Column(db.Integer, db.ForeignKey("fish_detections.id"), nullable=False, index=True)
    class_name = db.Column(db.String(32), nullable=False, default="fish")
    confidence = db.Column(db.Float, nullable=False)
    x1 = db.Column(db.Float, nullable=False)
    y1 = db.Column(db.Float, nullable=False)
    x2 = db.Column(db.Float, nullable=False)
    y2 = db.Column(db.Float, nullable=False)
    track_id = db.Column(db.Integer, nullable=True, index=True)

    def to_dict(self):
        return {
            "class": self.class_name,
            "confidence": self.confidence,
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "track_id": self.track_id,
        }
