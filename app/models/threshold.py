from datetime import datetime

from app.extensions import db


class Threshold(db.Model):
    __tablename__ = "thresholds"

    id = db.Column(db.Integer, primary_key=True)
    parameter = db.Column(db.String(64), unique=True, nullable=False)
    minimum_value = db.Column(db.Float, nullable=True)
    maximum_value = db.Column(db.Float, nullable=True)
    warning_level = db.Column(db.Float, nullable=True)
    critical_level = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(16), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "parameter": self.parameter,
            "minimum": self.minimum_value,
            "maximum": self.maximum_value,
            "warning_level": self.warning_level,
            "critical_level": self.critical_level,
            "unit": self.unit,
            "updated_at": self.updated_at.isoformat(),
        }

    def status_for(self, value):
        """minimum/maximum bound the Normal range; warning_level/critical_level are
        margins beyond that range at which the status escalates."""
        if value is None:
            return "Unknown"

        distance = 0.0
        if self.minimum_value is not None and value < self.minimum_value:
            distance = self.minimum_value - value
        elif self.maximum_value is not None and value > self.maximum_value:
            distance = value - self.maximum_value
        else:
            return "Normal"

        if self.critical_level is not None and distance >= self.critical_level:
            return "Critical"
        if self.warning_level is not None and distance >= self.warning_level:
            return "Warning"
        return "Warning" if distance > 0 else "Normal"
