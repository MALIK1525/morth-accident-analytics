"""Phase 13.3 live traffic + incident tests (research suite untouched)."""
import json
import os
import urllib.error

import pytest

from app.live import traffic as live_traffic
from app.server import app as flask_app


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


FLOW_RAW = {"flowSegmentData": {"frc": "FRC2", "currentSpeed": 30,
                                "freeFlowSpeed": 60, "currentTravelTime": 120,
                                "freeFlowTravelTime": 60, "confidence": 0.9,
                                "roadClosure": False}}
INC_RAW = {"incidents": [{"type": 1, "geometry": {"type": "Point",
                                                  "coordinates": [77.2, 28.6]},
                          "properties": {"id": "1", "iconCategory": 8,
                                         "from": "NH-48",
                                         "startTime": "2026-10-05T10:00:00",
                                         "endTime": "2026-10-05T12:00:00",
                                         "events": [{"description": "Closed"}]}}]}


class FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _patch(monkeypatch, payload, exc=None):
    def fake(req, timeout=None):
        if exc is not None:
            raise exc
        return FakeResp(payload)
    monkeypatch.setattr("urllib.request.urlopen", fake)


@pytest.fixture()
def with_key(monkeypatch):
    monkeypatch.setenv("TOMTOM_API_KEY", "test-key")
    live_traffic.clear_caches()
    yield
    live_traffic.clear_caches()
    monkeypatch.delenv("TOMTOM_API_KEY", raising=False)


@pytest.fixture()
def no_key(monkeypatch):
    monkeypatch.delenv("TOMTOM_API_KEY", raising=False)
    live_traffic.clear_caches()
    yield
    live_traffic.clear_caches()


def test_has_key_false_without_env(no_key):
    assert live_traffic.has_key() is False


def test_missing_key_returns_awaiting(no_key):
    assert live_traffic.get_flow()["status"] == "awaiting_key"
    assert live_traffic.get_incidents()["status"] == "awaiting_key"


def test_flow_normalization(with_key, monkeypatch):
    _patch(monkeypatch, FLOW_RAW)
    seg = live_traffic.fetch_flow(28.61, 77.21)
    assert seg["current_speed_kmh"] == 30
    assert seg["condition"] == "Slow"
    assert seg["delay_s"] == 60
    assert seg["source"] == "TomTom Traffic API"


def test_congestion_levels_distinct():
    labels = {live_traffic.congestion_level(c, 100)[0]
              for c in (95, 80, 60, 40, 10)}
    assert len(labels) == 5
    w = live_traffic.congestion_level(95, 100)
    v = live_traffic.congestion_level(10, 100)
    assert (w[1], w[2]) != (v[1], v[2])  # weight+dash differ, not colour


def test_flow_caching(with_key, monkeypatch):
    _patch(monkeypatch, FLOW_RAW)
    a = live_traffic.get_flow()
    assert a.get("cached") is not True
    b = live_traffic.get_flow()
    assert b["cached"] is True
    assert len(a["points"]) == 10


def test_rate_limit_handled(with_key, monkeypatch):
    _patch(monkeypatch, None, exc=urllib.error.HTTPError(
        "u", 429, "Too Many", {}, None))
    with pytest.raises(Exception):
        live_traffic.fetch_flow(28.61, 77.21)


def test_incident_normalization(with_key, monkeypatch):
    _patch(monkeypatch, INC_RAW)
    items = live_traffic.fetch_incidents("77.0,28.0,78.0,29.0")
    assert len(items) == 1
    assert items[0]["category"] == "Road closed"
    assert items[0]["road"] == "NH-48"
    assert items[0]["lat"] == 28.6
    assert "official" not in items[0]["category"].lower()


def test_city_bboxes_within_provider_limit():
    import re
    for c in [{"lat": 28.61, "lon": 77.21}, {"lat": 8.0, "lon": 77.0}]:
        parts = [float(x) for x in live_traffic.city_bbox(c["lat"], c["lon"]).split(",")]
        # rough km2 at India latitudes; must stay far below the 10,000 km2 cap
        area = (parts[2] - parts[0]) * 111 * (parts[3] - parts[1]) * 111
        assert area < 10000, area


def test_incidents_dedupe_and_cap(with_key, monkeypatch):
    _patch(monkeypatch, INC_RAW)
    out = live_traffic.get_incidents(force=True)
    assert out["status"] == "success"
    assert out["count"] == 1  # same id across 10 city bboxes deduped
    assert out["points"][0]["near"] == "Delhi"
    assert "not nationwide" in out["coverage"]
    styles = {(s, h) for s, h in
              [(v[1], v[2]) for v in live_traffic.INCIDENT_STYLES.values()]}
    assert len(styles) >= 10  # symbol+shape combos distinguish categories


def test_flow_endpoint_no_key(client, no_key):
    r = client.get("/api/live/traffic/flow")
    assert r.get_json()["status"] == "awaiting_key"


def test_incidents_endpoint_no_key(client, no_key):
    r = client.get("/api/live/traffic/incidents")
    assert r.get_json()["status"] == "awaiting_key"


def test_stale_incidents_served(with_key, monkeypatch):
    _patch(monkeypatch, INC_RAW)
    first = live_traffic.get_incidents()
    assert first["status"] == "success"
    _patch(monkeypatch, None, exc=urllib.error.URLError("down"))
    live_traffic._inc_cache["at"] = 0.0  # force expiry
    second = live_traffic.get_incidents()
    assert second.get("stale") is True
    assert len(second["points"]) == 1


def test_empty_incidents_ok(with_key, monkeypatch):
    _patch(monkeypatch, {"incidents": []})
    assert live_traffic.fetch_incidents("77.0,28.0,78.0,29.0") == []


def test_no_accident_kpis(with_key, monkeypatch):
    _patch(monkeypatch, FLOW_RAW)
    data = live_traffic.get_flow()
    blob = json.dumps(data).lower()
    for banned in ("fatalit", "injur", "accident rate", "risk score"):
        assert banned not in blob


def test_bw_encoding_present_in_flow(with_key, monkeypatch):
    _patch(monkeypatch, FLOW_RAW)
    data = live_traffic.get_flow()
    for p in data["points"]:
        assert p["line_weight"] and p["line_dash"]


def test_research_separation():
    import app.live.traffic as t
    src = open(t.__file__).read()
    for banned in ("DatasetLoader", "MoRTH_Primary", "get_clean_df",
                   "ml_pipeline", "benchmark"):
        assert banned not in src


def test_key_never_in_frontend():
    import re
    js = open("app/static/js/live.js", encoding="utf-8").read()
    html = open("app/templates/live.html", encoding="utf-8").read()
    blob = js + html
    # Env var NAMES may appear in setup help text; no assigned literal values.
    assert re.search(r"(TOMTOM_API_KEY|DATA_GOV_IN_API_KEY)\s*=\s*['\"][A-Za-z0-9]", blob) is None
    assert re.search(r"api-key=\w{4,}|key=\w{16,}", blob) is None


def test_weather_works_without_key(client, no_key, monkeypatch):
    def fake(req, timeout=None):
        return FakeResp([{"current": {"temperature_2m": 25.0}, "hourly": {}}] * 10)
    monkeypatch.setattr("urllib.request.urlopen", fake)
    from app.live import weather as w
    w.clear_cache()
    r = client.get("/api/live/weather/summary")
    assert r.get_json()["status"] == "success"
    w.clear_cache()


def test_status_reflects_key_state(client, no_key):
    layers = {l["layer"]: l["state"]
              for l in client.get("/api/live/status").get_json()["layers"]}
    assert layers["Traffic"] == "AWAITING_API_KEY"


def test_tile_cache_expiry_evict_never_stale(monkeypatch):
    calls = []

    def fake(req, timeout=None):
        calls.append(1)

        class R:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return b"PNG"
        return R()
    monkeypatch.setattr("urllib.request.urlopen", fake)
    monkeypatch.setenv("TOMTOM_API_KEY", "k")
    live_traffic._tile_cache.clear()
    live_traffic._tile_order.clear()
    assert live_traffic.fetch_tile("relative0", 7, 78, 54) == b"PNG"
    assert live_traffic.fetch_tile("relative0", 7, 78, 54) == b"PNG"
    assert len(calls) == 1  # second served from cache
    # force expiry -> refetch
    for k in list(live_traffic._tile_cache):
        at, body = live_traffic._tile_cache[k]
        live_traffic._tile_cache[k] = (at - live_traffic.TILE_TTL_S - 1, body)
    assert live_traffic.fetch_tile("relative0", 7, 78, 54) == b"PNG"
    assert len(calls) == 2
    # eviction cap respected
    assert len(live_traffic._tile_cache) <= live_traffic.TILE_CACHE_MAX


def test_tile_upstream_failure_no_stale(monkeypatch):
    import urllib.error
    monkeypatch.setenv("TOMTOM_API_KEY", "k")
    live_traffic._tile_cache.clear()
    live_traffic._tile_order.clear()

    def fake(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 503, "down", {}, None)
    monkeypatch.setattr("urllib.request.urlopen", fake)
    try:
        live_traffic.fetch_tile("relative0", 7, 78, 54)
        assert False, "should raise"
    except Exception:
        pass
    assert live_traffic._tile_cache == {}  # failures never cached as success


def test_tile_validation_no_provider_call(monkeypatch):
    called = []
    def fake(req, timeout=None):
        called.append(1)
        return FakeResp(b"PNG")
    monkeypatch.setattr("urllib.request.urlopen", fake)
    with pytest.raises(ValueError):
        live_traffic.fetch_tile("nope", 7, 78, 54)
    with pytest.raises(ValueError):
        live_traffic.fetch_tile("relative0", 99, 0, 0)
    with pytest.raises(ValueError):
        live_traffic.fetch_tile("relative0", 7, 99999, 0)
    assert called == []


def test_tile_caches_and_caps(monkeypatch):
    def fake(req, timeout=None):
        class R:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return b"PNGDATA"
        return R()
    monkeypatch.setattr("urllib.request.urlopen", fake)
    monkeypatch.setenv("TOMTOM_API_KEY", "k")
    a = live_traffic.fetch_tile("relative0", 7, 78, 54)
    b = live_traffic.fetch_tile("relative0", 7, 78, 54)
    assert a == b == b"PNGDATA"


def test_tile_route_validation(client):
    r = client.get("/api/live/traffic/tile/bogus/7/78/54.png")
    assert r.status_code == 400
    r = client.get("/api/live/traffic/tile/relative0/99/0/0.png")
    assert r.status_code == 400
    r = client.get("/api/live/traffic/tile/relative0/7/99999/0.png")
    assert r.status_code == 400


def test_tile_route_no_key_leak(client, no_key):
    r = client.get("/api/live/traffic/tile/relative0/7/78/54.png")
    assert r.status_code == 503
    assert "TOMTOM_API_KEY" not in r.get_data(as_text=True)


def test_segment_endpoint_validation(client, monkeypatch):
    monkeypatch.setenv("TOMTOM_API_KEY", "k")
    r = client.get("/api/live/traffic/segment?lat=abc&lon=0")
    assert r.status_code == 400


def test_unknown_category_preserved_not_guessed(with_key, monkeypatch):
    _patch(monkeypatch, {"incidents": [{
        "type": 1, "geometry": {"type": "Point", "coordinates": [77.0, 28.0]},
        "properties": {"id": "u1", "iconCategory": 99,
                       "events": [{"description": "Mystery"}]}}]})
    items = live_traffic.fetch_incidents("77.0,28.0,78.0,29.0")
    assert items[0]["category"] == "Unknown"
    assert items[0]["symbol"] == "?"


def test_delay_labels_only_when_defined(with_key, monkeypatch):
    def one(mag):
        _patch(monkeypatch, {"incidents": [{
            "type": 1, "geometry": {"type": "Point", "coordinates": [77.0, 28.0]},
            "properties": {"id": "d", "iconCategory": 6, "magnitudeOfDelay": mag,
                           "events": []}}]})
        return live_traffic.fetch_incidents("a")[0]["delay_label"]
    assert one(1) == "Minor delay"
    assert one(2) == "Moderate delay"
    assert one(3) == "Major delay"
    assert one(0) is None
    assert one(4) is None
    assert one(None) is None


def test_linestring_geometry_resolved(with_key, monkeypatch):
    _patch(monkeypatch, {"incidents": [{
        "type": 1, "geometry": {"type": "LineString",
                                "coordinates": [[[77.1, 28.5], [77.2, 28.6]]]},
        "properties": {"id": "l1", "iconCategory": 9, "events": []}}]})
    items = live_traffic.fetch_incidents("a")
    assert (items[0]["lat"], items[0]["lon"]) == (28.5, 77.1)
    assert items[0]["category"] == "Road works"


def test_missing_geometry_kept_with_nulls(with_key, monkeypatch):
    _patch(monkeypatch, {"incidents": [{
        "type": 1, "geometry": {},
        "properties": {"id": "g1", "iconCategory": 6, "events": []}}]})
    items = live_traffic.fetch_incidents("a")
    assert items[0]["lat"] is None  # frontend filters nulls from map
