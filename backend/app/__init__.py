import logging

from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .config import Config
from .game_data import load_sign_registry
from .ml.recognizer import ModelNotReady, load_recognizer
from .routes import api, error_response

log = logging.getLogger(__name__)


def create_app(overrides=None, recognizer=None, manifest=None) -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    app.config.update(overrides or {})
    app.json.sort_keys = False

    registry = load_sign_registry(app.config["SIGNS_PATH"])
    if recognizer is None:
        try:
            recognizer, manifest = load_recognizer(app.config["MODEL_DIR"], registry)
        except ModelNotReady as error:
            log.warning("model not ready: %s", error)
            recognizer, manifest = None, None
    app.extensions["pookie"] = {"registry": registry, "recognizer": recognizer, "manifest": manifest}

    CORS(app, resources={r"/api/validate-sign": {"origins": app.config["CORS_ORIGINS"]}}, methods=["POST"])
    app.register_blueprint(api)

    @app.errorhandler(HTTPException)
    def http_error(error):
        code = {404: "NOT_FOUND", 413: "UPLOAD_TOO_LARGE"}.get(error.code)
        body, _ = error_response(None, code or ("BAD_REQUEST" if error.code < 500 else "INTERNAL_ERROR"))
        return body, error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        log.error("unhandled error: %s", type(error).__name__)
        return error_response(None, "INTERNAL_ERROR")

    return app
