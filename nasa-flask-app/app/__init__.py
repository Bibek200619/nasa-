# app/__init__.py
import os, secrets
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # load .env in development

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Core config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    app.config["NASA_API_KEY"] = os.getenv("NASA_API_KEY")

    # Blueprints
    from app.main import bp as main_bp
    from app.apod import bp as apod_bp
    from app.rover import bp as rover_bp
    from app.gallery import bp as gallery_bp

    app.register_blueprint(main_bp)                     # "/" served by main
    app.register_blueprint(apod_bp, url_prefix="/apod")
    app.register_blueprint(rover_bp, url_prefix="/rover")
    app.register_blueprint(gallery_bp, url_prefix="/gallery")

    return app
