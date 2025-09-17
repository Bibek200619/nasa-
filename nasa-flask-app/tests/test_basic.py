# tests/test_basic.py
import pytest
from datetime import date

# ---------------------------
# Utilities
# ---------------------------

def _body(res):
    return res.data.decode("utf-8")

# ---------------------------
# Home
# ---------------------------

def test_home_ok(client):
    res = client.get("/")
    assert res.status_code == 200
    body = _body(res)
    assert "NASA Flask App" in body or "APOD" in body

# ---------------------------
# APOD
# ---------------------------

def test_apod_today_ok(client, monkeypatch):
    # Fake single APOD response (today)
    fake_apod = {
        "date": date.today().isoformat(),
        "title": "Test APOD Today",
        "media_type": "image",
        "url": "https://example.com/test_today.jpg",
        "explanation": "Test item.",
    }

    def fake_get_apod(apod_date=None, thumbs=True):
        return fake_apod

    # Routes import the nasa module (module-level), so patch module function
    monkeypatch.setattr("app.services.nasa.get_apod", fake_get_apod)

    res = client.get("/apod/")
    assert res.status_code == 200
    body = _body(res)
    assert "Test APOD Today" in body

def test_apod_specific_date_ok(client, monkeypatch):
    captured = {"called_with": None}

    def fake_get_apod(apod_date=None, thumbs=True):
        captured["called_with"] = {"apod_date": apod_date, "thumbs": thumbs}
        return {
            "date": "2024-01-01",
            "title": "Test APOD 2024-01-01",
            "media_type": "image",
            "url": "https://example.com/test_2024.jpg",
            "explanation": "Test item.",
        }

    monkeypatch.setattr("app.services.nasa.get_apod", fake_get_apod)

    res = client.get("/apod/?date=2024-01-01")
    assert res.status_code == 200
    body = _body(res)
    assert "Test APOD 2024-01-01" in body
    assert captured["called_with"] == {"apod_date": "2024-01-01", "thumbs": True}

def test_apod_invalid_date_rejected(client, monkeypatch):
    # If the route validates and rejects the date, service must not be called
    def should_not_call(*args, **kwargs):
        raise AssertionError("get_apod should not be called for invalid date")

    monkeypatch.setattr("app.services.nasa.get_apod", should_not_call)

    res = client.get("/apod/?date=1990-01-01")  # before APOD start
    assert res.status_code == 200
    body = _body(res)
    assert "Invalid APOD date" in body

def test_apod_video_thumbs_renders_thumbnail(client, monkeypatch):
    # Video entry should render thumbnail_url when thumbs=True
    def fake_get_apod(apod_date=None, thumbs=True):
        return {
            "date": "2024-01-02",
            "title": "Video Day",
            "media_type": "video",
            "url": "https://video.example.com/embed",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "explanation": "Video item.",
        }

    monkeypatch.setattr("app.services.nasa.get_apod", fake_get_apod)

    res = client.get("/apod/")
    assert res.status_code == 200
    body = _body(res)
    assert "Video Day" in body
    assert "example.com/thumb.jpg" in body  # expect thumbnail rendered for video

def test_apod_error_flash(client, monkeypatch):
    def fake_get_apod(apod_date=None, thumbs=True):
        raise Exception("403 Client Error: Forbidden")

    monkeypatch.setattr("app.services.nasa.get_apod", fake_get_apod)

    res = client.get("/apod/")
    assert res.status_code == 200
    body = _body(res)
    assert "Failed to load APOD" in body

# ---------------------------
# Mars Rover Photos
# ---------------------------

@pytest.mark.parametrize("rover", ["curiosity", "opportunity", "spirit", "perseverance"])
def test_rover_latest_by_each_rover_ok(client, monkeypatch, rover):
    def fake_latest(r="curiosity"):
        return [
            {
                "img_src": "https://example.com/latest.jpg",
                "earth_date": "2021-06-01",
                "sol": 100,
                "camera": {"full_name": "Navcam"},
                "rover": {"name": r.title()},
            }
        ]

    monkeypatch.setattr("app.services.nasa.get_latest_mars_photos", fake_latest)

    res = client.get(f"/rover/?mode=latest&rover={rover}")
    assert res.status_code == 200
    body = _body(res)
    assert rover.title() in body
    assert "Navcam" in body

def test_rover_by_sol_with_camera_ok(client, monkeypatch):
    captured = {"args": None}

    def fake_by_sol(rover, sol, camera=None):
        captured["args"] = {"rover": rover, "sol": sol, "camera": camera}
        return [
            {
                "img_src": "https://example.com/sol.jpg",
                "earth_date": "2021-06-01",
                "sol": sol,
                "camera": {"full_name": "Mast Camera"},
                "rover": {"name": rover.title()},
            }
        ]

    monkeypatch.setattr("app.services.nasa.get_mars_photos_by_sol", fake_by_sol)

    res = client.get("/rover/?mode=sol&rover=curiosity&sol=100&camera=mast")
    assert res.status_code == 200
    body = _body(res)
    assert "Mast Camera" in body
    assert captured["args"] == {"rover": "curiosity", "sol": 100, "camera": "mast"}

def test_rover_by_earth_date_with_camera_ok(client, monkeypatch):
    captured = {"args": None}

    def fake_by_date(rover, earth_date, camera=None):
        captured["args"] = {"rover": rover, "earth_date": earth_date, "camera": camera}
        return [
            {
                "img_src": "https://example.com/date.jpg",
                "earth_date": earth_date,
                "sol": 101,
                "camera": {"full_name": "RHAZ"},
                "rover": {"name": rover.title()},
            }
        ]

    monkeypatch.setattr("app.services.nasa.get_mars_photos_by_earth_date", fake_by_date)

    res = client.get("/rover/?mode=earth_date&rover=curiosity&earth_date=2021-06-01&camera=rhaz")
    assert res.status_code == 200
    body = _body(res)
    assert "RHAZ" in body
    assert captured["args"] == {"rover": "curiosity", "earth_date": "2021-06-01", "camera": "rhaz"}

def test_rover_error_flash(client, monkeypatch):
    def boom(*a, **k):
        raise Exception("backend error")

    monkeypatch.setattr("app.services.nasa.get_latest_mars_photos", boom)

    res = client.get("/rover/?mode=latest&rover=curiosity")
    assert res.status_code == 200
    body = _body(res)
    assert "Failed to load Mars photos" in body

# ---------------------------
# APOD Gallery (range)
# ---------------------------

def test_gallery_range_ok(client, monkeypatch):
    def fake_range(start_date, end_date, thumbs=True):
        return [
            {
                "date": start_date,
                "title": "Range Start",
                "media_type": "image",
                "url": "https://example.com/start.jpg",
            },
            {
                "date": end_date,
                "title": "Range End",
                "media_type": "video",
                "thumbnail_url": "https://example.com/end_thumb.jpg",
                "url": "https://example.com/video",
            },
        ]

    monkeypatch.setattr("app.services.nasa.get_apod_range", fake_range)

    res = client.get("/gallery/?start_date=2024-01-01&end_date=2024-01-02")
    assert res.status_code == 200
    body = _body(res)
    assert "Range Start" in body
    assert "Range End" in body
    assert "end_thumb.jpg" in body  # expect thumbnail used for video

def test_gallery_swaps_inverted_range_and_calls_once(client, monkeypatch):
    calls = []

    def fake_range(start_date, end_date, thumbs=True):
        calls.append((start_date, end_date, thumbs))
        return []

    monkeypatch.setattr("app.services.nasa.get_apod_range", fake_range)

    # Provide inverted dates; route should normalize (swap) before calling
    res = client.get("/gallery/?start_date=2024-01-05&end_date=2024-01-01")
    assert res.status_code == 200
    assert len(calls) == 1
    # Expect the service call to be with normalized (swapped) order
    assert calls[0] == ("2024-01-01", "2024-01-05", True)

def test_gallery_invalid_dates_rejected(client, monkeypatch):
    def should_not_call(*a, **k):
        raise AssertionError("get_apod_range should not be called for invalid dates")

    monkeypatch.setattr("app.services.nasa.get_apod_range", should_not_call)

    # Start before APOD archive start -> should flash error and not call
    res = client.get("/gallery/?start_date=1990-01-01&end_date=1990-01-02")
    assert res.status_code == 200
    body = _body(res)
    assert "Invalid start_date" in body

# ---------------------------
# Not Found
# ---------------------------

def test_404(client):
    res = client.get("/definitely-not-a-route")
    assert res.status_code == 404
