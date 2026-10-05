"""Phase 13.5 hardening tests: UX structure, TTLs, isolation, security."""
import re

from app.live import traffic as live_traffic
from app.live import watch as live_watch
from app.live import weather as live_weather
from app.server import app as flask_app


def _html():
    flask_app.config["TESTING"] = True
    return flask_app.test_client().get("/live").get_data(as_text=True)


def test_sections_and_toggles_present():
    html = _html()
    for token in ("India Live Map", "lyr-weather", "lyr-traffic", "lyr-incidents",
                  "Current Weather", "Traffic legend", "Incident markers",
                  "Government Data Watch", "LIVE DATA AVAILABILITY",
                  "wflt-geo", "wflt-exp", "hazards", "layer-ages"):
        assert token in html, token


def test_ephemeral_history_disclosed():
    assert "ephemeral" in _html()


def test_no_accident_kpi_language():
    html = _html().lower()
    for banned in ("accidents today", "live fatalities", "fatalities today",
                   "risk score", "accident rate", "predicted accident"):
        assert banned not in html, banned


def test_ttl_values_sane():
    assert live_weather.CACHE_TTL_S == 300
    assert live_traffic.FLOW_TTL_S == 120
    assert live_traffic.INCIDENT_TTL_S == 180
    assert live_traffic.FLOW_TTL_S < live_weather.CACHE_TTL_S


def test_incident_cap_present():
    js = open("app/static/js/live.js", encoding="utf-8").read()
    assert "slice(0, 300)" in js


def test_marker_shape_classes():
    html = _html()
    for cls in ("wx-circle", "wx-square", "wx-triangle", "wx-diamond",
                "wx-star", "wx-hexagon"):
        assert cls in html, cls


def test_responsive_map_css():
    html = _html()
    assert "@media" in html and "360px" in html


def test_history_gitignored():
    raw = open(".gitignore", "rb").read().decode("utf-8-sig", errors="replace")
    assert "scan_history" in raw


def test_no_secrets_in_live_code():
    blob = ""
    for f in ("app/live/weather.py", "app/live/traffic.py", "app/live/watch.py",
              "app/live/routes.py", "app/static/js/live.js",
              "app/templates/live.html"):
        blob += open(f, encoding="utf-8").read()
    assert re.search(r"sk-[A-Za-z0-9]{8,}", blob) is None
    assert re.search(r"api[-_]?key\s*=\s*['\"][A-Za-z0-9]{8,}", blob) is None
    # The env var NAME may appear, but never with an assigned literal value.
    for i, line in enumerate(blob.splitlines()):
        if "TOMTOM_API_KEY" in line or "DATA_GOV_IN_API_KEY" in line:
            assert re.search(r"(TOMTOM_API_KEY|DATA_GOV_IN_API_KEY)\s*=\s*['\"]", line) is None, \
                f"line {i}: {line.strip()[:100]}"


def test_watch_confined_to_review_queue():
    src = open("app/live/watch.py", encoding="utf-8").read()
    assert "REVIEW_DIR" in src
    assert "02_VERIFIED_DATA" not in src


def test_hazards_derive_only_from_feeds():
    js = open("app/static/js/live.js", encoding="utf-8").read()
    assert "drawHazards" in js
    assert "road_closure" in js and "Thunderstorm" in js


def test_watch_section_full_width():
    html = _html()
    assert 'id="watch-section"' in html
    # watch section must NOT be nested inside the 3-col map grid: it closes before it
    assert html.index("/grid: map + sidebar") < html.index('id="watch-section"')


def test_watch_summary_cards_filters_pagination():
    html = _html()
    for token in ("wsum-new", "wsum-upd", "wsum-tot", "wsum-src",
                  "btn-wclear", "btn-wmore", "xl:grid-cols-4"):
        assert token in html, token
    js = open("app/static/js/live.js", encoding="utf-8").read()
    assert "WATCH_PAGE = 12" in js
    assert "Clear Filters" in html or "btn-wclear" in html


def test_watch_status_icon_system():
    js = open("app/static/js/live.js", encoding="utf-8").read()
    for token in ("WSTATUS", "SOURCE_UNAVAILABLE", "EXPOSURE CANDIDATE",
                  "requires validation before any risk-rate"):
        assert token in js, token


def test_status_layers_complete():
    flask_app.config["TESTING"] = True
    layers = flask_app.test_client().get("/api/live/status").get_json()["layers"]
    names = {l["layer"] for l in layers}
    assert {"Weather", "Traffic", "Reported incidents",
            "Official accident records", "Government data watch"} <= names
