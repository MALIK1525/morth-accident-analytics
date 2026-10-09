"""Phase 16 acceptance tests: India map, state intel, near-me, crime filter."""
import json

from app.server import app as flask_app


def _client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def _norm(s):
    import re
    return re.sub(r"\s+", " ", (s or "").lower().replace("&", "and")).strip()


def test_geojson_vendored_and_sourced():
    import os
    p = "app/static/geo/india_states.geojson"
    assert os.path.exists(p)
    assert os.path.getsize(p) < 1_000_000
    fc = json.load(open(p, encoding="utf-8"))
    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 36
    assert "datameet" in json.dumps(fc.get("properties", {})).lower()


def test_geo_covers_benchmark_entities():
    fc = json.load(open("app/static/geo/india_states.geojson", encoding="utf-8"))
    geo = {_norm(f["properties"]["name"]) for f in fc["features"]}
    need = {"telangana", "ladakh", "odisha", "uttarakhand",
            "dadra and nagar haveli and daman and diu"}
    assert need <= geo, need - geo


def test_state_intel_endpoint():
    d = _client().get("/api/live/state-intel").get_json()
    assert d["status"] == "success"
    assert len(d["states"]) == 38
    up = d["states"]["Uttar Pradesh"]
    assert up["latest_year"] == 2024
    assert up["latest"]["accidents"] > 0
    assert up["severity_per_100"] == round(
        up["latest"]["fatalities"] / up["latest"]["accidents"] * 100, 2)
    assert "NOT live" in d["note"] or "not live" in d["note"].lower()


def test_injured_missing_is_null_not_zero():
    d = _client().get("/api/live/state-intel").get_json()
    nulls = [s for s, v in d["states"].items()
             if v["years"].get(2024, {}).get("injured") is None]
    assert nulls, "expected unpublished 2023-24 state injuries"
    for s, v in d["states"].items():
        for y, m in v["years"].items():
            assert m["injured"] is None or isinstance(m["injured"], int)


def test_no_state_carries_national_total():
    d = _client().get("/api/live/state-intel").get_json()
    for s, v in d["states"].items():
        assert v["latest"]["accidents"] < 487707, s


def test_map_ui_elements_present():
    html = _client().get("/live").get_data(as_text=True)
    for token in ("state-search", "btn-india-reset", "state-panel",
                      "btn-near-me", "near-me", "india_map.js"):
        assert token in html, token
    js = open("app/static/js/india_map.js", encoding="utf-8").read()
    assert "/static/geo/india_states.geojson" in js


def test_geolocation_opt_in_only():
    js = open("app/static/js/india_map.js", encoding="utf-8").read()
    assert "getCurrentPosition" in js
    assert js.index("btn-near-me") < js.index("getCurrentPosition")
    assert "analytics" not in js.lower()
    assert "localStorage" not in js and "sessionStorage" not in js


def test_crime_filtered_by_default():
    html = _client().get("/live").get_data(as_text=True)
    assert "<option selected>RELEVANT</option>" in html


def test_traffic_setup_instructions():
    html = _client().get("/live").get_data(as_text=True)
    js = open("app/static/js/live.js", encoding="utf-8").read()
    assert "TOMTOM_API_KEY" in js and "Environment" in js


def test_diagnostics_no_secrets():
    d = _client().get("/api/live/status").get_json()
    diag = d["diagnostics"]
    assert diag["tomtom_key_configured"] is False
    blob = json.dumps(d)
    assert "TOMTOM_API_KEY\", \"" not in blob


def test_benchmark_checksum_unchanged():
    import hashlib
    import pathlib
    h = hashlib.sha256(pathlib.Path(
        "data/MoRTH_Primary_Dataset_3.xlsx").read_bytes()).hexdigest()
    assert h == "d8064caab5302bb13314210fe13166ad80c9d3d7a27e7db35e3e5fde08474fb1"


def test_india_map_js_separation():
    src = open("app/static/js/india_map.js", encoding="utf-8").read()
    for banned in ("DatasetLoader", "get_clean_df", "ml_pipeline"):
        assert banned not in src
