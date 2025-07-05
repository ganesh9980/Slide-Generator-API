from flask import Flask
from .config import Config

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Required for non-app context initialization
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    limiter.init_app(app)
    limiter.default_limits = ["200 per day", "50 per hour"]

    from app.controllers import presentation_controller
    app.register_blueprint(presentation_controller.bp)

    return app