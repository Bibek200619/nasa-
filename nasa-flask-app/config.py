# config.py
import os

class Config:
    NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-prod")
    JSONIFY_PRETTYPRINT_REGULAR = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
