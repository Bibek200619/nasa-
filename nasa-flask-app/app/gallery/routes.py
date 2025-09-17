# app/gallery/routes.py
from flask import render_template, request, flash
from datetime import date, datetime
from app.gallery import bp
import app.services.nasa as nasa  # module import for easy monkeypatching

APOD_START = date(1995, 6, 16)

def _parse(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None

@bp.route("/", methods=["GET"])
def gallery_page():
    start_in = request.args.get("start_date")
    end_in = request.args.get("end_date")

    items, err = [], None
    start_date = _parse(start_in) if start_in else None
    end_date = _parse(end_in) if end_in else None

    if start_date and (start_date < APOD_START or start_date > date.today()):
        flash("Invalid start_date: use YYYY-MM-DD between 1995-06-16 and today", "error")
        start_date = None
    if end_date and (end_date < APOD_START or end_date > date.today()):
        flash("Invalid end_date: use YYYY-MM-DD between 1995-06-16 and today", "error")
        end_date = None

    if start_date and end_date and start_date > end_date:
        start_date, end_date = end_date, start_date
        flash("Dates swapped to form a valid range", "info")

    if start_date and end_date:
        try:
            items = nasa.get_apod_range(start_date.isoformat(), end_date.isoformat(), thumbs=True)
            items.sort(key=lambda x: x.get("date", ""), reverse=True)
        except Exception as e:
            err = str(e)
            flash("Failed to load APOD gallery", "error")

    return render_template(
        "gallery/gallery.html",
        items=items,
        start_date=start_date.isoformat() if start_date else (start_in or ""),
        end_date=end_date.isoformat() if end_date else (end_in or ""),
        error=err,
    )
