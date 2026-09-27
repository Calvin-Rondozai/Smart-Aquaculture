import os

from flask import Blueprint, abort, current_app, send_from_directory

media_bp = Blueprint("media", __name__)

_ALLOWED_SUBDIRS = {"processed", "camera", "exports"}


@media_bp.route("/media/<subdir>/<path:filename>")
def serve_media(subdir, filename):
    if subdir not in _ALLOWED_SUBDIRS:
        abort(404)
    directory = os.path.join(current_app.config["STORAGE_DIR"], subdir)
    return send_from_directory(directory, filename)
