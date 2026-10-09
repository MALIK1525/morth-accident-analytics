"""Phase 13.2 Live Monitor tests (research suite untouched)."""
import io
import json
import urllib.error

import pytest

from app.live import weather as live_weather
from app.server import app as flask_app


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


SAMPLE_RAW = {
    "current": {"time": "2026-10-05T18:00", "temperature_2m": 28.5,
                "relative_humidity_2m": 62, "precipitation": 0.0,
                "weather_code": 2, "wind_speed_10m": 11.2,
                "wind_direction_10m": 300},
    "hourly": {"visibility": [None, 10000, 9500]},
}


class FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _patch(monkeypatch, payload=SAMPLE_RAW, exc=None):
    def fake(req, timeout=None):
        if exc is not None:
            raise exc
        return FakeResp(payload)
    monkeypatch.setattr("urllib.request.urlopen", fake)


def test_fetch_valid_response(monkeypatch):
    _patch(monkeypatch)
    obs = live_weather.fetch_point(28.61, 77.21)
    assert obs["temperature_c"] == 28.5
    assert obs["humidity_pct"] == 62
    assert obs["condition"] == "Partly cloudy"
    assert obs["visibility_m"] == 9500
    assert obs["source"] == "Open-Meteo"


def test_missing_fields_return_none(monkeypatch):
    _patch(monkeypatch, {"current": {}, "hourly": {}})
    obs = live_weather.fetch_point(28.61, 77.21)
    assert obs["temperature_c"] is None
    assert obs["visibility_m"] is None
    assert obs["condition"] == "Not available"


def test_invalid_coordinates_rejected():
    with pytest.raises(ValueError):
        live_weather.fetch_point(999, 0)


def test_api_failure_raises(monkeypatch):
    _patch(monkeypatch, exc=urllib.error.URLError("down"))
    with pytest.raises(Exception):
        live_weather.fetch_point(28.61, 77.21)


def test_timeout_propagates(monkeypatch):
    import socket
    _patch(monkeypatch, exc=socket.timeout("t"))
    with pytest.raises(Exception):
        live_weather.fetch_point(28.61, 77.21)


def test_stale_fallback_serves_last_good(monkeypatch):
    from app.live import weather as w
    w.clear_cache()
    good = {"status": "success", "source": "Open-Meteo", "fetched_at": "t",
            "points": [{"name": "Delhi", "temperature_c": 30.0}],
            "failed": [], "summary": {}}
    w._cache.update(at=0.0, data=good)

    def boom(req, timeout=None):
        raise OSError("net down")
    monkeypatch.setattr("urllib.request.urlopen", boom)
    out = w.get_summary(force=True)
    assert out.get("stale") is True
    assert len(out["points"]) == 1
    w.clear_cache()


def test_fetch_retries_then_raises(monkeypatch):
    from app.live import weather as w
    calls = []

    def boom(req, timeout=None):
        calls.append(1)
        raise OSError("net down")
    monkeypatch.setattr("urllib.request.urlopen", boom)
    monkeypatch.setattr("time.sleep", lambda s: None)
    try:
        w._fetch("http://example.com")
        assert False, "should raise"
    except OSError:
        pass
    assert len(calls) == 2


def test_summary_math_and_cache(monkeypatch):
    live_weather.clear_cache()
    _patch(monkeypatch)
    s1 = live_weather.get_summary()
    assert s1["summary"]["locations_monitored"] == 10
    assert s1["summary"]["rain_affected"] == 0
    assert s1["summary"]["avg_temp_c"] == 28.5
    s2 = live_weather.get_summary()  # cache hit, no fetch
    assert s2["cached"] is True
    live_weather.clear_cache()


def test_point_endpoint(client, monkeypatch):
    _patch(monkeypatch)
    r = client.get("/api/live/weather?lat=28.61&lon=77.21")
    assert r.status_code == 200
    assert r.get_json()["temperature_c"] == 28.5


def test_point_endpoint_bad_coords(client):
    r = client.get("/api/live/weather?lat=abc&lon=0")
    assert r.status_code == 400


def test_status_badges(client):
    layers = {l["layer"]: l["state"]
              for l in client.get("/api/live/status").get_json()["layers"]}
    assert layers["Weather"] == "AVAILABLE"
    assert layers["Official accident records"] == "NOT_AVAILABLE"


def test_research_separation():
    import app.live.routes as routes
    import app.live.weather as w
    src = open(routes.__file__).read() + open(w.__file__).read()
    for banned in ("DatasetLoader", "MoRTH_Primary", "get_clean_df", "ml_pipeline"):
        assert banned not in src


def test_no_fabricated_values(monkeypatch):
    _patch(monkeypatch, {"current": {"temperature_2m": 30.0}, "hourly": {}})
    obs = live_weather.fetch_point(28.61, 77.21)
    assert obs["humidity_pct"] is None  # never zero-filled/invented
    assert obs["wind_speed_kmh"] is None


def test_live_page_loads(client):
    r = client.get("/live")
    assert r.status_code == 200
    assert "LIVE ROAD SAFETY MONITOR" in r.get_data(as_text=True)
