# app/main/__init__.py
from flask import Blueprint
bp = Blueprint("main", __name__, template_folder="../templates/main")
from app.main import routes
