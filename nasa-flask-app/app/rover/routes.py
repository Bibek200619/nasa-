# app/rover/routes.py
from flask import render_template, request, flash
from app.rover import bp
import app.services.nasa as nasa  # module import for easy monkeypatching

ROVERS = ["curiosity", "opportunity", "spirit", "perseverance"]
CAMERAS = ["fhaz", "rhaz", "mast", "chemcam", "mahli", "mardi", "navcam", "pancam", "minites"]

@bp.route("/", methods=["GET"])
def rover_page():
    rover = (request.args.get("rover") or "curiosity").lower()
    mode = request.args.get("mode", "latest")
    camera = request.args.get("camera") or None
    sol = request.args.get("sol", type=int)
    earth_date = request.args.get("earth_date") or None

    photos, err = [], None
    try:
        if mode == "latest":
            photos = nasa.get_latest_mars_photos(rover)
        elif mode == "sol" and sol is not None:
            photos = nasa.get_mars_photos_by_sol(rover, sol, camera)
        elif mode == "earth_date" and earth_date:
            photos = nasa.get_mars_photos_by_earth_date(rover, earth_date, camera)
        else:
            photos = nasa.get_latest_mars_photos(rover)
    except Exception as e:
        err = str(e)
        flash("Failed to load Mars photos", "error")

    return render_template(
        "rover/rover.html",
        photos=photos,
        rover=rover,
        mode=mode,
        cameras=CAMERAS,
        rovers=ROVERS,
        error=err,
    )
