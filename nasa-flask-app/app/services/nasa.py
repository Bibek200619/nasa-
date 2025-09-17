# app/services/nasa.py
import os
import requests
from flask import current_app

# Endpoints
BASE_APOD = "https://api.nasa.gov/planetary/apod"
BASE_ROVER = "https://api.nasa.gov/mars-photos/api/v1"

def _api_key() -> str:
    key = current_app.config.get("NASA_API_KEY") or os.getenv("NASA_API_KEY")
    return key.strip() if isinstance(key, str) else key

def _get(url: str, params: dict, timeout: int = 20) -> requests.Response:
    r = requests.get(url, params=params, timeout=timeout)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        print(
            f"HTTP {r.status_code} | "
            f"X-RateLimit-Remaining={r.headers.get('X-RateLimit-Remaining')} | "
            f"URL={r.url} | Body={r.text[:300]}"
        )
        raise
    return r

# ---------- APOD ----------
def get_apod(apod_date: str | None = None, thumbs: bool = True) -> dict:
    params = {"api_key": _api_key(), "thumbs": "true" if thumbs else "false"}
    if apod_date:
        params["date"] = apod_date  # YYYY-MM-DD
    return _get(BASE_APOD, params, timeout=15).json()

def get_apod_range(start_date: str, end_date: str, thumbs: bool = True) -> list[dict]:
    params = {
        "api_key": _api_key(),
        "start_date": start_date,
        "end_date": end_date,
        "thumbs": "true" if thumbs else "false",
    }
    data = _get(BASE_APOD, params, timeout=20).json()
    return data if isinstance(data, list) else [data]

# ---------- Mars Rover Photos ----------
def get_latest_mars_photos(rover: str = "curiosity") -> list[dict]:
    url = f"{BASE_ROVER}/rovers/{rover}/latest_photos"
    params = {"api_key": _api_key()}
    return _get(url, params).json().get("latest_photos", [])

def get_mars_photos_by_sol(rover: str, sol: int, camera: str | None = None) -> list[dict]:
    url = f"{BASE_ROVER}/rovers/{rover}/photos"
    params = {"api_key": _api_key(), "sol": sol}
    if camera:
        params["camera"] = camera
    return _get(url, params).json().get("photos", [])

def get_mars_photos_by_earth_date(rover: str, earth_date: str, camera: str | None = None) -> list[dict]:
    url = f"{BASE_ROVER}/rovers/{rover}/photos"
    params = {"api_key": _api_key(), "earth_date": earth_date}
    if camera:
        params["camera"] = camera
    return _get(url, params).json().get("photos", [])
