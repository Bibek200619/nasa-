# app/gallery/__init__.py
from flask import Blueprint
bp = Blueprint("gallery", __name__, template_folder="../templates/gallery")
from app.gallery import routes
