# app/rover/__init__.py
from flask import Blueprint
bp = Blueprint("rover", __name__, template_folder="../templates/rover")
from app.rover import routes
