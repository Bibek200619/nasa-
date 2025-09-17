# app/apod/__init__.py
from flask import Blueprint
bp = Blueprint("apod", __name__, template_folder="../templates/apod")
from app.apod import routes
