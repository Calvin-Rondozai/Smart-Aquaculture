from datetime import datetime

from app.extensions import db
from app.models import Alert


def create_alert(alert_type, severity, message, parameter=None, value=None, dedupe=True):
    """Creates an alert unless an unresolved alert of the same type+parameter
    already exists (avoids spamming the same warning every polling cycle)."""
    if dedupe:
        existing = Alert.query.filter_by(
            type=alert_type, parameter=parameter, resolved=False
        ).first()
        if existing:
            return existing

    alert = Alert(
        type=alert_type,
        severity=severity,
        message=message,
        parameter=parameter,
        value=value,
    )
    db.session.add(alert)
    db.session.commit()
    return alert


def resolve_alert(alert_id):
    alert = Alert.query.get(alert_id)
    if alert is None:
        return None
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    return alert


def auto_resolve(alert_type, parameter=None):
    """Resolves any open alert of this type/parameter — used when a
    condition that triggered an alert has cleared (e.g. device back online,
    reading back in normal range)."""
    query = Alert.query.filter_by(type=alert_type, resolved=False)
    if parameter is not None:
        query = query.filter_by(parameter=parameter)
    open_alerts = query.all()
    for alert in open_alerts:
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
    if open_alerts:
        db.session.commit()
    return open_alerts


def check_water_quality(parameter, value, threshold):
    """Given a Threshold row for `parameter`, raises/clears alerts based on
    the reading's status."""
    if threshold is None or value is None:
        return

    status = threshold.status_for(value)
    if status == "Critical":
        create_alert(
            "water_quality_critical",
            "critical",
            f"{parameter.replace('_', ' ').title()} is critically outside the configured range.",
            parameter=parameter,
            value=value,
        )
    elif status == "Warning":
        create_alert(
            "water_quality_warning",
            "warning",
            f"{parameter.replace('_', ' ').title()} is outside the configured normal range.",
            parameter=parameter,
            value=value,
        )
    else:
        auto_resolve("water_quality_critical", parameter=parameter)
        auto_resolve("water_quality_warning", parameter=parameter)


def check_device_status(device):
    status = device.status()
    if status == "Offline":
        create_alert(
            "device_offline",
            "warning",
            f"Device '{device.device_id}' has gone offline.",
            parameter=device.device_id,
        )
    else:
        auto_resolve("device_offline", parameter=device.device_id)
