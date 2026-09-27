from datetime import datetime

from app.extensions import db

ALERT_TYPES = (
    "water_quality_warning",
    "water_quality_critical",
    "device_offline",
    "camera_offline",
    "ai_analysis_failure",
    "low_detection_confidence",
)

SEVERITIES = ("info", "warning", "critical")


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64), nullable=False)
    severity = db.Column(db.String(16), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    parameter = db.Column(db.String(64), nullable=True)
    value = db.Column(db.Float, nullable=True)
    resolved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "severity": self.severity,
            "message": self.message,
            "parameter": self.parameter,
            "value": self.value,
            "resolved": self.resolved,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
