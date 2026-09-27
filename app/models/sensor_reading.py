from datetime import datetime

from app.extensions import db


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), db.ForeignKey("devices.device_id"), nullable=False, index=True)
    temperature = db.Column(db.Float, nullable=True)
    ph = db.Column(db.Float, nullable=True)
    dissolved_oxygen = db.Column(db.Float, nullable=True)
    turbidity = db.Column(db.Float, nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "temperature": self.temperature,
            "ph": self.ph,
            "dissolved_oxygen": self.dissolved_oxygen,
            "turbidity": self.turbidity,
            "recorded_at": self.recorded_at.isoformat(),
        }
