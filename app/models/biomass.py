from datetime import datetime

from app.extensions import db


class BiomassEstimate(db.Model):
    __tablename__ = "biomass_estimates"

    id = db.Column(db.Integer, primary_key=True)
    detection_id = db.Column(db.Integer, db.ForeignKey("fish_detections.id"), nullable=False, index=True)
    estimated_biomass = db.Column(db.Float, nullable=True)  # kg; null when unavailable
    method = db.Column(db.String(64), nullable=False, default="unavailable")
    confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            "estimated_biomass": self.estimated_biomass,
            "unit": "kg",
            "method": self.method,
            "confidence": self.confidence,
            "status": "unavailable" if self.estimated_biomass is None else "estimated",
            "created_at": self.created_at.isoformat(),
        }
