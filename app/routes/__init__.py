def register_blueprints(app):
    from app.routes.dashboard import dashboard_bp
    from app.routes.iot import iot_bp
    from app.routes.camera import camera_bp
    from app.routes.analytics import analytics_bp
    from app.routes.alerts import alerts_bp
    from app.routes.devices import devices_bp
    from app.routes.settings import settings_bp
    from app.routes.export import export_bp
    from app.routes.media import media_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(iot_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(media_bp)
