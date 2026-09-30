import logging

from flask import Flask, jsonify, render_template

from config import config_by_name


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    with app.app_context():
        _init_database(app)
        _init_fish_detection(app)

    return app


def _init_extensions(app):
    from app.extensions import db, cors

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})


def _register_blueprints(app):
    from app.routes import register_blueprints

    register_blueprints(app)


def _init_database(app):
    from app.extensions import db
    from app.models import Threshold

    db.create_all()
    _seed_default_thresholds(db, Threshold)


def _seed_default_thresholds(db, Threshold):
    """Seeds sane starting thresholds for a small-scale pond if none exist
    yet. These are editable via Settings — never hard-coded in the frontend
    (PRD Section 10 / Non-Negotiable Rule 10)."""
    defaults = [
        dict(parameter="temperature", minimum_value=24.0, maximum_value=30.0,
             warning_level=2.0, critical_level=4.0, unit="°C"),
        dict(parameter="ph", minimum_value=6.5, maximum_value=8.5,
             warning_level=0.5, critical_level=1.0, unit="pH"),
        dict(parameter="dissolved_oxygen", minimum_value=4.0, maximum_value=15.0,
             warning_level=1.0, critical_level=2.0, unit="mg/L"),
        dict(parameter="turbidity", minimum_value=0.0, maximum_value=50.0,
             warning_level=20.0, critical_level=50.0, unit="NTU"),
    ]
    for defaults_row in defaults:
        exists = Threshold.query.filter_by(parameter=defaults_row["parameter"]).first()
        if not exists:
            db.session.add(Threshold(**defaults_row))
    db.session.commit()


def _init_fish_detection(app):
    from app.services.fish_detection_service import fish_detection_service
    from app.services.tracking_service import fish_tracker

    fish_detection_service.init_app(app)  # loaded once at startup — never per-request
    fish_tracker.init_app(app)


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_error):
        if _wants_json():
            return jsonify({"success": False, "message": "Not found"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception(error)
        if _wants_json():
            return jsonify({"success": False, "message": "An internal error occurred"}), 500
        return render_template("errors/500.html"), 500

    def _wants_json():
        from flask import request

        return request.path.startswith("/api/")
