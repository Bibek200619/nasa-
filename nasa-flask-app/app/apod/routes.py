# app/apod/routes.py
from flask import render_template, request, flash
from datetime import date, datetime
from app.apod import bp
import app.services.nasa as nasa  # module import for easy monkeypatching

APOD_START = date(1995, 6, 16)

def _valid_date(s: str) -> bool:
    try:
        d = datetime.strptime(s, "%Y-%m-%d").date()
        return APOD_START <= d <= date.today()
    except Exception:
        return False

@bp.route("/", methods=["GET"])
def apod_page():
    apod_date = request.args.get("date") or None
    if apod_date and not _valid_date(apod_date):
        flash("Invalid APOD date: use YYYY-MM-DD between 1995-06-16 and today", "error")
        apod_date = None

    data, err = None, None
    try:
        data = nasa.get_apod(apod_date, thumbs=True)
    except Exception as e:
        err = str(e)
        flash(f"Failed to load APOD", "error")

    return render_template("apod/apod.html", apod=data, error=err)
