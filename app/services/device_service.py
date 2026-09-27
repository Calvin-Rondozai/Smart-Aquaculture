from app.extensions import db
from app.models import Device


def get_or_create_device(device_id, device_type, name=None, ip_address=None, firmware_version=None):
    device = Device.query.filter_by(device_id=device_id).first()
    if device is None:
        device = Device(
            device_id=device_id,
            name=name or device_id,
            device_type=device_type,
            ip_address=ip_address,
            firmware_version=firmware_version,
        )
        db.session.add(device)
    device.touch(ip_address=ip_address, firmware_version=firmware_version)
    db.session.commit()
    return device


def list_devices(offline_threshold_seconds):
    devices = Device.query.order_by(Device.device_id.asc()).all()
    return [d.to_dict(offline_threshold_seconds) for d in devices]


def get_device(device_id, offline_threshold_seconds):
    device = Device.query.filter_by(device_id=device_id).first()
    return device.to_dict(offline_threshold_seconds) if device else None


def get_device_model(device_id):
    return Device.query.filter_by(device_id=device_id).first()
