import os

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    # threaded=True: fish-detection inference can take several seconds on
    # CPU-only hardware — without this, that one request would block every
    # other page/API call for its duration (PRD Section 48).
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"], threaded=True)
